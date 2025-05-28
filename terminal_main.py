import warnings
warnings.filterwarnings('ignore')

from src.chat_interface import ChatInterface
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
import time

def print_welcome_message():
    console = Console()
    welcome_text = """
    🤖 Welcome to Personal Assistant Terminal Interface!
    
    I can help you with:
    • Managing your emails
    • Handling calendar events
    • And more!
    
    Type 'exit' or 'quit' to end the session.
    """
    console.print(Panel(welcome_text, title="Personal Assistant", border_style="blue"))

def main():
    console = Console()
    chat_interface = ChatInterface()
    
    # Print welcome message
    print_welcome_message()
    
    # Initialize conversation history
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            # Check for exit command
            if user_input.lower() in ['exit', 'quit']:
                console.print("\n[bold green]Thank you for using Personal Assistant! Goodbye! 👋[/bold green]")
                break
            
            # Process the input
            console.print("\n[bold yellow]Assistant is thinking...[/bold yellow]")
            response = chat_interface.process_user_input(user_input)
            
            # Print response with a slight delay for better UX
            time.sleep(0.5)
            console.print("\n[bold green]Assistant:[/bold green]")
            console.print(Markdown(response))
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            console.print("\n\n[bold red]Session interrupted. Goodbye![/bold red]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
            continue

if __name__ == "__main__":
    main() 