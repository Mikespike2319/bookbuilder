"""
Utility functions for the Novel Assistant CLI.
Provides reusable input handling and validation functions.
"""

def get_float_input(prompt, min_val, max_val, default):
    """
    Get a float input within specified range with validation.
    
    Args:
        prompt (str): The prompt to display to the user
        min_val (float): Minimum acceptable value
        max_val (float): Maximum acceptable value
        default (float): Default value if input is empty
        
    Returns:
        float: The validated input value
    """
    value = input(prompt).strip()
    if not value:
        return default
    
    try:
        float_val = float(value)
        if float_val < min_val:
            print(f"Value too low, setting to minimum ({min_val})")
            return min_val
        elif float_val > max_val:
            print(f"Value too high, setting to maximum ({max_val})")
            return max_val
        return float_val
    except ValueError:
        print(f"Invalid value, using default ({default})")
        return default

def get_yes_no_input(prompt):
    """
    Get a yes/no response from the user.
    
    Args:
        prompt (str): The prompt to display to the user
        
    Returns:
        bool: True if the user responded with 'y' or 'yes', False otherwise
    """
    response = input(prompt).strip().lower()
    return response == "y" or response == "yes"

def get_string_input(prompt, default=""):
    """
    Get a string input from the user with optional default.
    
    Args:
        prompt (str): The prompt to display to the user
        default (str): Default value if input is empty
        
    Returns:
        str: The user's input or the default value
    """
    value = input(prompt).strip()
    return value if value else default