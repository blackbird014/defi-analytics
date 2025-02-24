from src.interfaces.iagent import IAgent

class ExampleAgent(IAgent):
    def execute(self) -> None:
        # Agent-specific execution logic
        print("Executing example agent")

    def get_name(self) -> str:
        return "Example Agent"

    def get_description(self) -> str:
        return "This is an example agent that demonstrates the IAgent interface implementation" 