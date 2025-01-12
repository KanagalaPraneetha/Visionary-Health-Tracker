def handle_navigation(command):
    """Handle navigation commands from voice input"""
    command = command.lower()
    
    nav_commands = {
        'go to camera': '/camera',
        'show settings': '/settings',
        'go home': '/',
        'show dashboard': '/'
    }
    
    return nav_commands.get(command, '/')