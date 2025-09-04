# app/main.py
from __future__ import annotations
import os, json, sys
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.rule import Rule
from rich import box

from .prompts import SYSTEM_PROMPT
from .llm import gen_final_answer
from .router import route_message
from .context import load_context, save_context, to_context_card, merge_router_into_context
from .external_api import geocode_city, fetch_weather_summary, country_info_by_name

console = Console()
load_dotenv()

def call_tools(router_json: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    tool_results = {}
    destination = ctx.get("destination")
    
    # Weather
    if router_json.get("needs_weather") and destination:
        try:
            geo = geocode_city(destination)
            if geo:
                wx = fetch_weather_summary(geo["lat"], geo["lon"])
                tool_results["geocode"] = geo
                tool_results["weather"] = wx
            else:
                tool_results["geocode"] = None
                tool_results["weather"] = None
                console.print(f"[yellow]⚠️  Could not find location data for '{destination}'[/yellow]")
        except Exception as e:
            tool_results["geocode"] = None
            tool_results["weather"] = None
            console.print(f"[red]⚠️  Weather service unavailable: {str(e)[:50]}...[/red]")
    
    # Country info (based on geocode.country if available)
    if router_json.get("needs_country_info"):
        try:
            country_name = None
            if "geocode" in tool_results and tool_results["geocode"] and tool_results["geocode"].get("country"):
                country_name = tool_results["geocode"]["country"]
            elif destination:
                # fall back: try using destination as country (not perfect)
                country_name = destination
            if country_name:
                tool_results["country_info"] = country_info_by_name(country_name)
            else:
                tool_results["country_info"] = None
        except Exception as e:
            tool_results["country_info"] = None
            console.print(f"[red]⚠️  Country info service unavailable: {str(e)[:50]}...[/red]")
    
    return tool_results

def interactive_chat(session: str):
    store = load_context(session)
    ctx = store.get(session)  # dict
    
    # Welcome banner
    console.print(Panel.fit(
        "[bold cyan]✈️  Voyage Travel Assistant[/bold cyan]\n" +
        "[dim]Your AI-powered travel planning companion[/dim]\n\n" +
        "[yellow]Commands:[/yellow] [dim]'exit' or 'quit' to end, 'context' to view current trip info[/dim]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    
    while True:
        # Custom prompt with Rich
        user_message = Prompt.ask("[bold green]✨[/bold green]")
        
        if not user_message:
            continue
            
        if user_message.strip().lower() in {"exit", "quit"}:
            console.print(Panel(
                "[bold cyan]Thanks for using Voyage! Have a great trip! 🌟[/bold cyan]",
                border_style="cyan"
            ))
            break
            
        if user_message.strip().lower() == "context":
            display_context(ctx)
            continue

        # Show processing with spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task1 = progress.add_task("[cyan]Analyzing your message...", total=None)
            
            context_card = to_context_card(ctx)
            router_json = route_message(context_card, user_message)
            
            progress.update(task1, description="[cyan]Updating context...")
            ctx = merge_router_into_context(ctx, router_json)
            save_context(session, ctx)
            
            progress.update(task1, description="[cyan]Gathering travel data...")
            tool_results = call_tools(router_json, ctx)
            
            progress.update(task1, description="[cyan]Crafting your response...")
            context_card = to_context_card(ctx)
            reply = gen_final_answer(SYSTEM_PROMPT, context_card, router_json, tool_results, user_message)
        
        # Display response in a panel
        console.print(Panel(
            Markdown(reply),
            title="[bold blue]🗺️  Voyage",
            border_style="blue",
            box=box.ROUNDED
        ))
        
        # Show updated context if destination changed
        if router_json.get("destinations"):
            console.print("[dim]📍 Context updated[/dim]")
        
        console.print()  # Add spacing

def display_context(ctx: Dict[str, Any]):
    """Display current context in a formatted panel"""
    context_card = to_context_card(ctx)
    console.print(Panel(
        context_card,
        title="[bold yellow]📋 Current Trip Context",
        border_style="yellow",
        box=box.ROUNDED
    ))

def main():
    """Run the Travel Assistant"""
    # Simple argument parsing
    session = "default"
    message = None
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg in ["-s", "--session"] and i + 1 < len(sys.argv):
                session = sys.argv[i + 1]
            elif arg in ["-m", "--message"] and i + 1 < len(sys.argv):
                message = sys.argv[i + 1]
    
    store = load_context(session)
    ctx = store.get(session)

    if message:
        console.print(f"[bold cyan]Session:[/bold cyan] {session}")
        console.print(Rule(style="dim"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Processing your request...", total=None)
            
            context_card = to_context_card(ctx)
            router_json = route_message(context_card, message)
            
            progress.update(task, description="[cyan]Updating context...")
            ctx = merge_router_into_context(ctx, router_json)
            save_context(session, ctx)
            
            progress.update(task, description="[cyan]Gathering data...")
            tool_results = call_tools(router_json, ctx)
            
            progress.update(task, description="[cyan]Generating response...")
            context_card = to_context_card(ctx)
            reply = gen_final_answer(SYSTEM_PROMPT, context_card, router_json, tool_results, message)
        
        console.print(Panel(
            Markdown(reply),
            title="[bold blue]🗺️  Voyage Response",
            border_style="blue",
            box=box.ROUNDED
        ))
        return

    interactive_chat(session)

if __name__ == "__main__":
    main()
