import asyncio
from app.agent import app

async def run():
    print("Starting JobReady Agent in CLI Mode...")
    # Send START
    response = await app.execute(
        input_data=None,
        session_id="test_session",
    )
    
    # It should pause at intake
    print(f"\nAgent output:\n{response}")
    
    context = input("\n[HITL] Enter your career context: ")
    
    # Send context
    response = await app.execute(
        input_data=context,
        session_id="test_session",
    )
    print(f"\nAgent output:\n{response}")

if __name__ == "__main__":
    asyncio.run(run())
