"""
UI utilities for CLI: colored output, progress indicators, formatted messages.
"""
from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich import box

console = Console()


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[red]✗[/red] {message}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def format_health_check_result(result: dict[str, Any], show_json: bool = False) -> None:
    """
    Format health check results with colored output.
    If show_json is True, also print raw JSON.
    """
    checks = result.get("checks", {})
    overall_ok = result.get("ok", False)
    
    # Overall status panel
    status_color = "green" if overall_ok else "red"
    status_text = "✓ All required checks passed" if overall_ok else "✗ Some required checks failed"
    console.print(Panel(
        Text(status_text, style=status_color),
        title="Health Check Status",
        border_style=status_color
    ))
    
    # Checks table
    table = Table(title="Check Results", box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    for check_name, check_result in checks.items():
        passed = check_result.get("pass", False)
        detail = check_result.get("detail", {})
        
        # Format status
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        
        # Format details
        detail_str = ""
        if detail:
            parts = []
            for key, value in detail.items():
                if key == "error":
                    parts.append(f"Error: {value}")
                elif key == "missing":
                    if isinstance(value, list) and value:
                        parts.append(f"Missing: {', '.join(value)}")
                else:
                    parts.append(f"{key}: {value}")
            detail_str = "; ".join(parts)
        
        table.add_row(
            check_name.replace("_", " ").title(),
            status,
            detail_str or "—"
        )
    
    console.print(table)
    
    # Show JSON if requested
    if show_json:
        console.print("\n[dim]Raw JSON output:[/dim]")
        import json
        console.print(json.dumps(result, indent=2))


def format_status_result(status_data: dict[str, Any]) -> None:
    """Format status command output with colored display."""
    if "status" in status_data and status_data["status"] == "no_executions":
        console.print("[yellow]No executions found.[/yellow]")
        return
    
    last = status_data.get("last", {})
    if not last:
        console.print("[yellow]No execution data available.[/yellow]")
        return
    
    # Status panel
    status = last.get("status", "unknown")
    status_color = {
        "completed": "green",
        "failed": "red",
        "in_progress": "yellow",
        "pending": "blue"
    }.get(status.lower(), "white")
    
    console.print(Panel(
        Text(status.upper(), style=status_color),
        title="Last Execution Status",
        border_style=status_color
    ))
    
    # Details table
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    execution_id = last.get("id", "N/A")
    start_time = last.get("start_time", "N/A")
    end_time = last.get("end_time", "N/A")
    current_stage = last.get("current_stage", "N/A")
    error_message = last.get("error_message")
    cost_total = last.get("cost_total")
    
    table.add_row("Execution ID", str(execution_id))
    table.add_row("Status", f"[{status_color}]{status}[/{status_color}]")
    table.add_row("Start Time", str(start_time))
    table.add_row("End Time", str(end_time))
    table.add_row("Current Stage", str(current_stage))
    if cost_total is not None:
        table.add_row("Total Cost", f"${cost_total:.4f}")
    if error_message:
        table.add_row("Error", f"[red]{error_message}[/red]")
    
    console.print(table)


def create_progress_tracker(total_steps: int) -> Progress:
    """Create a progress tracker for pipeline execution."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )


def print_agent_progress(agent_name: str, step: int, total: int) -> None:
    """Print progress for a specific agent."""
    percentage = int((step / total) * 100)
    console.print(f"[cyan]→[/cyan] [{step}/{total}] {agent_name}... [{percentage}%]")


def print_pipeline_start() -> None:
    """Print pipeline start message."""
    console.print(Panel(
        Text("Starting YouTube Shorts Generation Pipeline", style="bold cyan"),
        border_style="cyan"
    ))


def print_pipeline_complete(execution_id: int) -> None:
    """Print pipeline completion message."""
    console.print(Panel(
        Text(f"✓ Pipeline completed successfully (Execution ID: {execution_id})", style="bold green"),
        border_style="green"
    ))


def print_pipeline_error(error: str) -> None:
    """Print pipeline error message."""
    console.print(Panel(
        Text(f"✗ Pipeline failed: {error}", style="bold red"),
        border_style="red"
    ))
