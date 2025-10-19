from dotenv import load_dotenv
from agents import ProspectSearchAgent

load_dotenv()

print("="*60)
print("Testing ProspectSearchAgent")
print("="*60)

agent = ProspectSearchAgent("test", "", [])

result = agent.execute({
    "icp": {
        "industry": "SaaS",
        "location": "USA",
        "employee_count": {"min": 100, "max": 1000},
        "revenue": {"min": 20000000, "max": 200000000}
    },
    "signals": ["recent_funding"]
})

print(f"\n✅ Found {len(result.get('leads', []))} leads")

if result.get('leads'):
    print("\nSample leads:")
    for i, lead in enumerate(result['leads'][:3], 1):
        print(f"{i}. {lead['contact_name']} at {lead['company']}")
        print(f"   Email: {lead['email']}")
        print(f"   Signal: {lead['signal']}")
else:
    print("\n⚠️  No leads found")
    print("This is expected if Apollo API is not configured")
    print("The system will use mock data for the full workflow")

print("="*60)