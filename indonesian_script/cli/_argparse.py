# args.py
import sys
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from colorama import init, Fore as f, Style as s

init()

class Colors:
    """Warna untuk CLI output"""
    ERROR = f.RED + s.BRIGHT
    SUCCESS = f.GREEN + s.BRIGHT
    WARNING = f.YELLOW + s.BRIGHT
    INFO = f.CYAN + s.BRIGHT
    DIM = f.CYAN + s.DIM
    BRIGHT_GREEN = f.GREEN + s.BRIGHT
    BRIGHT_CYAN = f.CYAN + s.BRIGHT
    RESET = s.RESET_ALL
    
    @staticmethod
    def error(text): return f"{Colors.ERROR}{text}{Colors.RESET}"
    @staticmethod
    def success(text): return f"{Colors.SUCCESS}{text}{Colors.RESET}"
    @staticmethod
    def warning(text): return f"{Colors.WARNING}{text}{Colors.RESET}"
    @staticmethod
    def info(text): return f"{Colors.INFO}{text}{Colors.RESET}"
    @staticmethod
    def dim(text): return f"{Colors.DIM}{text}{Colors.RESET}"
    @staticmethod
    def white(text): return f"{f.WHITE}{text}{Colors.RESET}"
    @staticmethod
    def bright_green(text): return f"{Colors.BRIGHT_GREEN}{text}{Colors.RESET}"
    @staticmethod
    def bright_cyan(text): return f"{Colors.BRIGHT_CYAN}{text}{Colors.RESET}"


class Argument:
    """Representasi single argument/option"""
    def __init__(
        self,
        *names: str,
        help: str = "",
        required: bool = False,
        default: Any = None,
        action: str = "store",
        choices: Optional[List[Any]] = None,
        nargs: Optional[Union[int, str]] = None,
        metavar: Optional[str] = None
    ):
        self.names = list(names)
        self.help = help
        self.required = required
        self.default = default
        self.action = action
        self.choices = choices
        self.nargs = nargs
        self.metavar = metavar
        self.value = default
        self.dest = self._get_dest()
    
    def _get_dest(self) -> str:
        """Get destination name from argument names"""
        for name in self.names:
            if name.startswith('--'):
                return name.lstrip('--').replace('-', '_')
            elif name.startswith('-'):
                return name.lstrip('-')
        return self.names[0]
    
    def _get_display_names(self) -> str:
        """Get display names for help"""
        return Colors.white(", ").join([Colors.bright_cyan(name) for name in self.names])
    
    def __repr__(self):
        return f"Argument({self.names}, dest={self.dest})"


class Command:
    """Representasi subcommand"""
    def __init__(self, name: str, help: str = "", aliases: Optional[List[str]] = None):
        self.name = name
        self.help = help
        self.aliases = aliases or []
        self.arguments: List[Argument] = []
        self.subcommands: Dict[str, 'Command'] = {}
        self.parent: Optional['Command'] = None
    
    def add_argument(self, *args, **kwargs):
        """Add argument to command"""
        arg = Argument(*args, **kwargs)
        self.arguments.append(arg)
        return arg
    
    def add_command(self, name: str, help: str = "", aliases: Optional[List[str]] = None) -> 'Command':
        """Add subcommand"""
        cmd = Command(name, help, aliases)
        cmd.parent = self
        self.subcommands[name] = cmd
        for alias in aliases or []:
            self.subcommands[alias] = cmd
        return cmd
    
    def _get_all_names(self) -> str:
        """Get all names including aliases"""
        if self.aliases:
            return f"{self.name}{Colors.white(', ')}{Colors.white(', ').join([Colors.bright_cyan(alias) for alias in self.aliases])}"
        return self.name


class ArgumentParser:
    """Main argument parser inspired by UV with minimal help interface"""
    def __init__(self, prog, description: str = "", epilog: str = ""):
        self.description = description
        self.epilog = epilog
        self.root_command = Command("", "Root command")
        self.global_arguments: List[Argument] = []
        self.prog = prog
    
    def add_argument(self, *args, **kwargs):
        """Add global argument"""
        arg = Argument(*args, **kwargs)
        self.global_arguments.append(arg)
        return arg
    
    def add_command(self, name: str, help: str = "", aliases: Optional[List[str]] = None) -> Command:
        """Add top-level command"""
        return self.root_command.add_command(name, help, aliases)
    
    def _format_usage(self, cmd: Optional[Command] = None) -> str:
        """Format usage line"""
        parts = [f"{Colors.bright_green('Usage')}: {Colors.bright_cyan(self.prog)}"]
        
        if self.global_arguments:
            parts.append(f"{Colors.dim('[OPTIONS]')}")
        
        if cmd and cmd.name:
            parts.append(f"{Colors.bright_cyan(cmd.name)}")
        
            if cmd and cmd.arguments:
                for arg in cmd.arguments:
                    if arg.names and not arg.names[0].startswith('-'):
                        # Positional argument
                        metavar = arg.metavar or arg.names[0].upper().strip('<>')
                        parts.append(f"{Colors.dim(f'<{metavar}>')}")
        
            if cmd and cmd.subcommands:
                parts.append(f"{Colors.dim('<COMMAND>')}")
            if cmd and cmd.arguments:
                parts.append(f"{Colors.dim('<OPTIONS>')}")
        else:
            parts.append(f"{Colors.dim('<COMMAND>')}")
            
        return " ".join(parts)
    
    def _format_options(self, arguments: List[Argument], is_global: bool = False) -> List[str]:
        """Format options section"""
        if not arguments:
            return []
        
        lines = []
        label = "Global Options" if is_global else "Options"
        lines.append(f"{Colors.bright_green(label)}:")
        
        for arg in arguments:
            # Display names
            display = f"  {Colors.bright_cyan(arg._get_display_names())}"
            
            # Add metavar if exists
            if arg.metavar and arg.names and arg.names[0].startswith('-'):
                display += f" {Colors.dim(f'<{arg.metavar}>')}"
            
            lines.append(display)
            
            # Description with indent 4 spaces
            desc = arg.help
            if arg.choices:
                desc += f"{s.BRIGHT} [choices: {", ".join(map(Colors.bright_cyan, arg.choices))}]"
            if arg.default is not None and arg.action != "store_true":
                desc += f"{s.BRIGHT} [default: {Colors.bright_cyan(arg.default)}{Colors.RESET}{s.NORMAL}]"
            
            if desc:
                lines.append(f"    {Colors.white(desc)}")
        
        lines.append("")
        return lines
    
    def _format_commands(self, commands: Dict[str, Command]) -> List[str]:
        """Format commands section"""
        if not commands:
            return []
        
        lines = [f"{Colors.bright_green('Commands:')}"]
        
        # Unique commands (not aliases)
        seen = set()
        unique_cmds = []
        for name, cmd in commands.items():
            if cmd.name in seen:
                continue
            seen.add(cmd.name)
            unique_cmds.append(cmd)
        
        for cmd in unique_cmds:
            display = f"  {Colors.bright_cyan(cmd._get_all_names())}"
            lines.append(display)
            if cmd.help:
                lines.append(f"    {Colors.white(cmd.help)}")
        
        lines.append("")
        return lines
    
    def _format_arguments(self, arguments: List[Argument]) -> List[str]:
        """Format arguments section for commands"""
        pos_args = [arg for arg in arguments if arg.names and not arg.names[0].startswith('-')]
        if not pos_args:
            return []
        
        lines = [f"{Colors.bright_green('Arguments:')}"]
        
        for arg in pos_args:
            metavar = arg.metavar or arg.names[0].upper().strip('<>')
            display = f"  {Colors.dim(f'<{metavar}>')}"
            lines.append(display)
            if arg.help:
                lines.append(f"    {Colors.white(arg.help)}")
        
        lines.append("")
        return lines
    
    def print_help(self, cmd: Optional[Command] = None, error_msg: Optional[str] = None):
        """Print help with minimal format like UV"""
        
        print(self.description)
        print()
        
        if error_msg:
            print(f"{Colors.error('error:')} {error_msg}")
            print()
        
        # Usage
        print(self._format_usage(cmd))
        print()
        
        if cmd and cmd.name:
            # Arguments
            for line in self._format_arguments(cmd.arguments):
                print(line)
            
            # Command options
            opt_args = [arg for arg in cmd.arguments if arg.names and arg.names[0].startswith('-')]
            if opt_args:
                for line in self._format_options(opt_args, is_global=False):
                    print(line)
            
            # Command help
            if self.global_arguments:
                for line in self._format_options(self.global_arguments, is_global=True):
                    print(line)
            
            # Subcommands
            if cmd.subcommands:
                for line in self._format_commands(cmd.subcommands):
                    print(line)
        else:
            # Commands
            if self.root_command.subcommands:
                for line in self._format_commands(self.root_command.subcommands):
                    print(line)
            
            # Root help
            if self.global_arguments:
                for line in self._format_options(self.global_arguments, is_global=True):
                    print(line)
            
        
        if error_msg:
            print(f"{Colors.white('For more information, try')} '{Colors.bright_cyan('--help')}'{Colors.white('.')}")
    
    def _parse_value(self, value: str, argument: Argument) -> Any:
        """Parse argument value with type conversion"""
        if argument.choices and value not in argument.choices:
            self._error(f"invalid value '{value}' for {argument._get_display_names()}: choose from {argument.choices}")
        return value
    
    def _error(self, message: str, show_usage: bool = True):
        """Show error and exit"""
        print(f"{Colors.error('error:')} {message}")
        print()
        if show_usage:
            print(self._format_usage())
            print()
            print(f"{Colors.white('For more information, try')} '{Colors.bright_cyan('--help')}'{Colors.white('.')}")
        sys.exit(1)
    
    def _parse_args(self, args: List[str], cmd: Command, parsed: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Recursively parse arguments"""
        i = 0
        combined_args = cmd.arguments + self.global_arguments
        
        while i < len(args):
            arg = args[i]
            
            # Help
            if arg in ['-h', '--help']:
                self.print_help(cmd if cmd.name else None)
                sys.exit(0)
            
            # Check for subcommands
            if arg in cmd.subcommands:
                subcmd = cmd.subcommands[arg]
                parsed['command'] = subcmd.name
                remaining = args[i+1:]
                return self._parse_args(remaining, subcmd, parsed)
            
            # Check for options
            found = False
            for argument in combined_args:
                if arg in argument.names:
                    # Handle argument value
                    if argument.action == "store_true":
                        argument.value = True
                        i += 1
                    elif argument.action == "store":
                        if i + 1 < len(args) and not args[i+1].startswith('-'):
                            argument.value = self._parse_value(args[i+1], argument)
                            i += 2
                        else:
                            self._error(f"argument {arg} requires a value")
                    found = True
                    break
            
            if not found:
                # Positional argument
                pos_args = [a for a in cmd.arguments if a.names and not a.names[0].startswith('-')]
                if pos_args:
                    pos_arg = pos_args[0]
                    if pos_arg.value == pos_arg.default:
                        pos_arg.value = self._parse_value(arg, pos_arg)
                        i += 1
                        found = True
                
                if not found:
                    if cmd.name:
                        self._error(f"unrecognized argument '{arg}'", show_usage=False)
                    else:
                        self._error(f"unrecognized subcommand '{arg}'")
        
        # Store values
        for arg in combined_args:
            if arg.value is not None and arg.value != arg.default:
                parsed[arg.dest] = arg.value
            elif arg.required:
                self._error(f"the following arguments are required: {arg._get_display_names()}")
            else:
                parsed[arg.dest] = arg.default
        
        return parsed, args[i:]
    
    def parse_args(self, args: Optional[List[str]] = None) -> Any:
        """Main parsing method"""
        if args is None:
            args = sys.argv[1:]
        
        parsed = {}
        
        # No arguments
        if not args:
            self.print_help()
            sys.exit(0)
        
        try:
            result, _ = self._parse_args(args, self.root_command, parsed)
            return Namespace(**result)
        except SystemExit:
            raise
        except Exception as e:
            self._error(str(e))
    
    def set_prog(self, prog: str):
        """Set program name"""
        self.prog = prog
    
    def help(self):
        self.print_help()

class Namespace:
    """Simple namespace for storing parsed arguments"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        items = sorted(self.__dict__.items())
        return f"Namespace({', '.join(f'{k}={v!r}' for k, v in items)})"