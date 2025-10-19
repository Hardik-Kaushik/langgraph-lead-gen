from .base_agent import BaseAgent
from typing import Dict, Any
import os

# Try to import OpenAI, but handle if not available or no credits
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class FeedbackTrainerAgent(BaseAgent):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only initialize LLM if OpenAI is available and has API key
        api_key = os.getenv("OPENAI_API_KEY")
        
        if OPENAI_AVAILABLE and api_key:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.3,
                    openai_api_key=api_key
                )
                self.use_llm = True
            except Exception as e:
                self.logger.warning(f"Could not initialize OpenAI: {str(e)}")
                self.llm = None
                self.use_llm = False
        else:
            self.logger.info("OpenAI not available, using basic recommendations")
            self.llm = None
            self.use_llm = False
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance and suggest improvements"""
        self.logger.info("Analyzing feedback and generating recommendations...")
        
        responses = inputs.get("responses", [])
        
        # Calculate metrics
        metrics = self._calculate_metrics(responses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, responses)
        
        # Log to Google Sheets (simulated)
        self._log_to_sheets(recommendations)
        
        output = {"recommendations": recommendations, "metrics": metrics}
        self.log_execution(inputs, output)
        
        return output
    
    def _calculate_metrics(self, responses: list) -> Dict:
        """Calculate campaign metrics"""
        total = len(responses)
        
        if total == 0:
            return {"open_rate": 0, "click_rate": 0, "reply_rate": 0, "meeting_rate": 0}
        
        metrics = {
            "open_rate": sum(1 for r in responses if r.get("opened")) / total,
            "click_rate": sum(1 for r in responses if r.get("clicked")) / total,
            "reply_rate": sum(1 for r in responses if r.get("replied")) / total,
            "meeting_rate": sum(1 for r in responses if r.get("meeting_booked")) / total
        }
        
        return metrics
    
    def _generate_recommendations(self, metrics: Dict, responses: list) -> list:
        """Generate improvement recommendations (uses LLM if available, otherwise basic logic)"""
        
        # Use basic recommendations if LLM not available or to avoid quota issues
        if not self.use_llm or not self.llm:
            return self._generate_basic_recommendations(metrics)
        
        # Try LLM-based recommendations, fallback to basic if error
        prompt = f"""
Analyze this email campaign performance and suggest 3 specific improvements:

Metrics:
- Open Rate: {metrics['open_rate']:.1%}
- Click Rate: {metrics['click_rate']:.1%}
- Reply Rate: {metrics['reply_rate']:.1%}
- Meeting Rate: {metrics['meeting_rate']:.1%}

Provide recommendations in this format:
1. [Category]: [Specific actionable recommendation]
2. [Category]: [Specific actionable recommendation]
3. [Category]: [Specific actionable recommendation]

Categories can be: Subject Line, Email Content, ICP Targeting, Timing, Personalization
"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            
            # Parse recommendations
            lines = content.strip().split("\n")
            recommendations = []
            
            for line in lines:
                if line.strip() and line[0].isdigit():
                    recommendations.append({
                        "recommendation": line.strip(),
                        "status": "pending_approval",
                        "metrics": metrics
                    })
            
            # Return LLM recommendations if we got at least one
            if recommendations:
                return recommendations
            else:
                # Fallback to basic if parsing failed
                return self._generate_basic_recommendations(metrics)
            
        except Exception as e:
            self.logger.error(f"Recommendation generation error: {str(e)}")
            # Fallback to basic recommendations
            return self._generate_basic_recommendations(metrics)
    
    def _generate_basic_recommendations(self, metrics: Dict) -> list:
        """Generate basic recommendations without LLM"""
        recommendations = []
        
        # Analyze open rate
        if metrics['open_rate'] < 0.3:
            recommendations.append({
                "recommendation": "1. Subject Line: Test more compelling subject lines to improve open rate (currently {:.1%})".format(metrics['open_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        elif metrics['open_rate'] > 0.5:
            recommendations.append({
                "recommendation": "1. Subject Line: Great open rate ({:.1%})! Continue A/B testing to optimize further".format(metrics['open_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        else:
            recommendations.append({
                "recommendation": "1. Subject Line: Decent open rate ({:.1%}). Test personalization tokens to increase".format(metrics['open_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        
        # Analyze reply rate
        if metrics['reply_rate'] < 0.1:
            recommendations.append({
                "recommendation": "2. Email Content: Low reply rate ({:.1%}). Add stronger CTAs and value propositions".format(metrics['reply_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        else:
            recommendations.append({
                "recommendation": "2. Email Content: Good engagement ({:.1%} reply rate). Focus on converting replies to meetings".format(metrics['reply_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        
        # Analyze meeting booking rate
        if metrics['meeting_rate'] < 0.1:
            recommendations.append({
                "recommendation": "3. ICP Targeting: Low meeting rate ({:.1%}). Review ICP criteria and refine targeting".format(metrics['meeting_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        else:
            recommendations.append({
                "recommendation": "3. ICP Targeting: Solid meeting rate ({:.1%}). Consider expanding to similar profiles".format(metrics['meeting_rate']),
                "status": "pending_approval",
                "metrics": metrics
            })
        
        return recommendations
    
    def _log_to_sheets(self, recommendations: list):
        """Log recommendations to Google Sheets"""
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            from datetime import datetime
            
            creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if not creds_path or not sheet_id or not os.path.exists(creds_path):
                self.logger.info("Google Sheets not configured, logging to console only")
                return
            
            # Authenticate
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            
            # Prepare data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            rows = []
            for rec in recommendations:
                metrics = rec.get("metrics", {})
                rows.append([
                    timestamp,
                    rec.get("campaign_id", "N/A"),
                    f"{metrics.get('open_rate', 0):.1%}",
                    f"{metrics.get('reply_rate', 0):.1%}",
                    rec.get("recommendation", ""),
                    rec.get("status", "pending")
                ])
            
            # Append to sheet
            body = {'values': rows}
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range='Sheet1!A:F',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.logger.info(f"✅ Logged {len(rows)} recommendations to Google Sheets")
            
        except ImportError:
            self.logger.info("Google Sheets libraries not installed, skipping...")
        except Exception as e:
            self.logger.warning(f"Could not log to Google Sheets: {str(e)}")