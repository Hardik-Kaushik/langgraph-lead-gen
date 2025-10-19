from .base_agent import BaseAgent
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

class OutreachContentAgent(BaseAgent):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized outreach messages"""
        self.logger.info("Generating outreach content...")
        
        ranked_leads = inputs.get("ranked_leads", [])
        persona = inputs.get("persona", "SDR")
        tone = inputs.get("tone", "friendly")
        
        messages = []
        
        # Take top 5 leads
        for lead in ranked_leads[:5]:
            message = self._generate_message(lead, persona, tone)
            messages.append(message)
        
        output = {"messages": messages}
        self.log_execution(inputs, output)
        
        return output
    
    def _generate_message(self, lead: Dict, persona: str, tone: str) -> Dict:
        """Generate personalized email for a lead"""
        
        prompt = ChatPromptTemplate.from_template("""
You are a {persona} writing a {tone} outreach email.

Lead Information:
- Company: {company}
- Contact: {contact}
- Role: {role}
- Technologies: {technologies}

Write a short, personalized email (max 100 words) that:
1. Shows you've done research on their company
2. Mentions a relevant pain point
3. Offers value from Analytos.ai (B2B analytics platform)
4. Has a clear CTA

Also create a compelling subject line.

Return in this format:
SUBJECT: [subject line]
BODY: [email body]
""")
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    persona=persona,
                    tone=tone,
                    company=lead.get("company", ""),
                    contact=lead.get("contact", ""),
                    role=lead.get("role", ""),
                    technologies=", ".join(lead.get("technologies", [])[:3])
                )
            )
            
            content = response.content
            
            # Parse subject and body
            lines = content.split("\n")
            subject = ""
            body = ""
            
            for line in lines:
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("BODY:"):
                    body = line.replace("BODY:", "").strip()
                elif body:  # Continue body if already started
                    body += " " + line.strip()
            
            return {
                "lead": lead.get("contact", ""),
                "email": lead.get("email", ""),
                "subject": subject or "Partnering with your team",
                "email_body": body or "Generic message placeholder"
            }
            
        except Exception as e:
            self.logger.error(f"Content generation error: {str(e)}")
            return {
                "lead": lead.get("contact", ""),
                "email": lead.get("email", ""),
                "subject": "Let's connect",
                "email_body": f"Hi {lead.get('contact', 'there')}, I'd love to discuss how we can help."
            }