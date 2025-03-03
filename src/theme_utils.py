"""
Theme utilities for Streamlit UI
Handles loading CSS, theme switching and other styling functionality
"""
import streamlit as st
import base64
from pathlib import Path

def load_css(css_file_path):
    """
    Load and inject a CSS file into Streamlit
    
    Args:
        css_file_path (str): Path to the CSS file
    """
    try:
        with open(css_file_path, 'r') as f:
            css = f'<style>{f.read()}</style>'
            st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load CSS file: {css_file_path}. Error: {e}")

def load_js(script):
    """
    Load and inject a JavaScript into Streamlit
    
    Args:
        script (str): JavaScript code to inject
    """
    js_code = f'<script>{script}</script>'
    st.markdown(js_code, unsafe_allow_html=True)

def inject_theme_switcher():
    """
    Inject JavaScript for theme switching functionality
    
    This adds a script that handles:
    - Saving theme preference in localStorage
    - Toggling between light and dark themes
    - Respecting system theme preference initially
    """
    theme_script = """
    // Theme switcher JavaScript
    document.addEventListener('DOMContentLoaded', (event) => {
        // Function to set theme
        function setTheme(themeName) {
            localStorage.setItem('theme', themeName);
            document.documentElement.setAttribute('data-theme', themeName);
            
            // Update toggle if it exists
            const toggleInput = document.getElementById('theme-toggle');
            if (toggleInput) {
                toggleInput.checked = themeName === 'dark';
            }
        }

        // Function to toggle between themes
        function toggleTheme() {
            if (localStorage.getItem('theme') === 'dark') {
                setTheme('light');
            } else {
                setTheme('dark');
            }
        }
        
        // Set initial theme or respect system preference
        function setInitialTheme() {
            const savedTheme = localStorage.getItem('theme');
            
            if (savedTheme) {
                setTheme(savedTheme);
            } else {
                const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
                setTheme(prefersDarkScheme ? 'dark' : 'light');
            }
        }
        
        // Call once to initialize
        setInitialTheme();
        
        // Add event listener to toggle if it exists
        document.addEventListener('click', function(e) {
            if (e.target && e.target.id === 'theme-toggle') {
                toggleTheme();
            }
        });
    });
    """
    load_js(theme_script)

def inject_theme_toggle_html():
    """
    Generate the HTML for a theme toggle switch
    
    Creates a toggle switch with sun and moon icons for light/dark mode
    """
    toggle_html = """
    <div class="theme-toggle">
        <span>☀️</span>
        <label for="theme-toggle">
            <input type="checkbox" id="theme-toggle">
            <span class="slider"></span>
        </label>
        <span>🌙</span>
    </div>
    """
    st.markdown(toggle_html, unsafe_allow_html=True)

def add_logo(logo_path, width=200):
    """
    Add a logo to the sidebar
    
    Args:
        logo_path (str): Path to the logo image file
        width (int, optional): Width of the logo in pixels. Defaults to 200.
    """
    if not Path(logo_path).exists():
        return
        
    logo_img = Path(logo_path).read_bytes()
    logo_b64 = base64.b64encode(logo_img).decode()
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_b64}" width="{width}px">
        </div>
        """,
        unsafe_allow_html=True,
    )

def add_page_transitions():
    """
    Add page transition animations
    
    Adds fade-in effect to the main container for smoother UX
    """
    transition_css = """
    <style>
    .main .block-container {
        animation: fadeIn 0.5s ease forwards;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
    """
    st.markdown(transition_css, unsafe_allow_html=True)

def setup_page_config(title="Open Gemini Deep Research", icon="🔍", layout="wide"):
    """
    Configure the page settings
    
    Args:
        title (str, optional): Page title. Defaults to "Open Gemini Deep Research".
        icon (str, optional): Page icon. Defaults to "🔍".
        layout (str, optional): Page layout. Defaults to "wide".
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )

def setup_theme(custom_css_path=None):
    """
    Complete theme setup including CSS, JS and theme toggle
    
    Args:
        custom_css_path (str, optional): Path to a custom CSS file to load in addition to the default.
    """
    # Inject base CSS fixes for consistent styling
    st.markdown("""
    <style>
    /* Base UI fixes */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        box-shadow: 0 0 0 2px rgba(75, 111, 255, 0.3);
    }
    /* Fix Streamlit elements */
    .css-1aumxhk {
        background-color: var(--bg-secondary);
    }
    /* Fix sidebar padding */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-main);
        border-right: 1px solid var(--border-color);
        padding: 10px;
    }
    /* Fix main padding */
    .main .block-container {
        padding-top: 30px;
        padding-bottom: 80px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Setup default CSS
    css_path = Path(__file__).parent.parent / "static" / "css" / "styles.css"
    if css_path.exists():
        load_css(str(css_path))
    else:
        st.warning(f"Default CSS file not found: {css_path}")
    
    # Load custom CSS if provided
    if custom_css_path and Path(custom_css_path).exists():
        load_css(custom_css_path)
    
    # Add theme toggle functionality
    inject_theme_switcher()
    
    # Add page transitions
    add_page_transitions()
    
def create_sidebar_header(title="Open Gemini", subtitle="Deep Research", include_toggle=True):
    """
    Create a styled sidebar header
    
    Args:
        title (str, optional): Header title. Defaults to "Open Gemini".
        subtitle (str, optional): Header subtitle. Defaults to "Deep Research".
        include_toggle (bool, optional): Whether to include the theme toggle. Defaults to True.
    """
    st.sidebar.markdown(f"""
    <div class="sidebar-header">
        <h2 style="margin:0; padding:0; font-weight:700;">🔍 {title}</h2>
        <h3 style="margin:0; padding:0; font-weight:500; opacity: 0.9;">{subtitle}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Add theme toggle to sidebar
    if include_toggle:
        st.sidebar.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
        inject_theme_toggle_html()

def add_custom_font(font_url):
    """
    Add a custom font using Google Fonts or any other font URL
    
    Args:
        font_url (str): URL to the font (e.g. Google Fonts URL)
    """
    st.markdown(
        f"""
        <link href="{font_url}" rel="stylesheet">
        """,
        unsafe_allow_html=True
    )

def add_font_awesome():
    """Add Font Awesome icons support"""
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        """,
        unsafe_allow_html=True
    )

def inject_css_variables(variables_dict):
    """
    Inject custom CSS variables to override the defaults
    
    Args:
        variables_dict (dict): Dictionary of CSS variables to override
            Example: {'--primary-color': '#ff0000', '--text-color': '#333333'}
    """
    css_vars = "\n".join([f"    {var}: {value} !important;" for var, value in variables_dict.items()])
    
    custom_css = f"""
    <style>
    :root {{
{css_vars}
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def apply_custom_theme(primary_color=None, success_color=None, warning_color=None, danger_color=None, 
                       text_color=None, bg_color=None):
    """
    Apply a custom theme by overriding default CSS variables
    
    Args:
        primary_color (str, optional): Primary brand color. Defaults to None.
        success_color (str, optional): Success/positive color. Defaults to None.
        warning_color (str, optional): Warning/caution color. Defaults to None.
        danger_color (str, optional): Danger/negative color. Defaults to None.
        text_color (str, optional): Main text color. Defaults to None.
        bg_color (str, optional): Background color. Defaults to None.
    """
    variables = {}
    
    if primary_color:
        variables['--primary-color'] = primary_color
        variables['--primary-light'] = f"{primary_color}19"  # 10% opacity
        variables['--primary-gradient'] = f"linear-gradient(135deg, {primary_color} 0%, {adjust_color_brightness(primary_color, -20)} 100%)"
    
    if success_color:
        variables['--success-color'] = success_color
        variables['--success-light'] = f"{success_color}19"  # 10% opacity
        
    if warning_color:
        variables['--warning-color'] = warning_color
        variables['--warning-light'] = f"{warning_color}19"  # 10% opacity
        
    if danger_color:
        variables['--danger-color'] = danger_color
        variables['--danger-light'] = f"{danger_color}19"  # 10% opacity
        
    if text_color:
        variables['--text-color'] = text_color
        variables['--text-secondary'] = adjust_color_brightness(text_color, 30)
        
    if bg_color:
        variables['--bg-main'] = bg_color
        variables['--bg-secondary'] = adjust_color_brightness(bg_color, -5)
        variables['--bg-tertiary'] = adjust_color_brightness(bg_color, -10)
        
    if variables:
        inject_css_variables(variables)

def adjust_color_brightness(color_hex, brightness_offset=0):
    """
    Adjust the brightness of a color
    
    Args:
        color_hex (str): Hex color code (e.g., '#ff0000')
        brightness_offset (int): Positive for lighter, negative for darker
        
    Returns:
        str: Adjusted hex color
    """
    if not color_hex.startswith('#'):
        return color_hex
        
    # This is a simplified version - a real implementation would convert to HSL,
    # adjust the lightness and convert back
    return color_hex