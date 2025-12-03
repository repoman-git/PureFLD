"""
Meridian Welcome Wizard

Onboarding flow for non-technical users.
"Meridian for Dummies" - Simple, friendly, click-through tutorial.
"""

import streamlit as st
from pathlib import Path


# Configuration
WIZARD_COMPLETE_FILE = Path(__file__).parent.parent.parent.parent / "data" / ".wizard_complete"


def mark_wizard_complete():
    """Mark wizard as completed"""
    WIZARD_COMPLETE_FILE.parent.mkdir(parents=True, exist_ok=True)
    WIZARD_COMPLETE_FILE.touch()


def is_wizard_complete():
    """Check if wizard has been completed"""
    return WIZARD_COMPLETE_FILE.exists()


st.set_page_config(
    page_title="Welcome to Meridian",
    page_icon="🌟",
    layout="centered"
)

# Initialize session state
if 'wizard_screen' not in st.session_state:
    st.session_state.wizard_screen = 1

screen = st.session_state.wizard_screen

# ═══════════════════════════════════════════════════════════════════
# SCREEN 1: WELCOME
# ═══════════════════════════════════════════════════════════════════

if screen == 1:
    st.title("🌟 Welcome to Meridian")
    
    st.markdown("## Your personal investment assistant")
    st.markdown("### *No maths, no coding, no stress.*")
    
    st.markdown("---")
    
    st.markdown("""
    Meridian helps you create a **safe, smart ETF investment portfolio** with a few clicks.
    
    You do not need to understand markets — **Meridian handles the complex work for you.**
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start", type="primary", use_container_width=True):
            st.session_state.wizard_screen = 2
            st.rerun()
    
    with col2:
        if st.button("Skip Wizard", use_container_width=True):
            mark_wizard_complete()
            st.info("Navigate to Dashboard from the sidebar →")

# ═══════════════════════════════════════════════════════════════════
# SCREEN 2: WHAT MERIDIAN DOES
# ═══════════════════════════════════════════════════════════════════

elif screen == 2:
    st.title("📊 What Meridian Does")
    
    st.markdown("## Meridian builds your portfolio automatically")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Analyzes ETFs")
        st.caption("Examines thousands of investment funds")
        
        st.markdown("### ✅ Combines them safely")
        st.caption("Balances growth with protection")
    
    with col2:
        st.markdown("### ✅ Tests scenarios")
        st.caption("Simulates crashes, inflation, recessions")
        
        st.markdown("### ✅ Generates your plan")
        st.caption("Personalized investment strategy")
    
    st.markdown("---")
    
    st.info("💡 **Meridian explains everything in simple language** — no jargon!")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back"):
            st.session_state.wizard_screen = 1
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.wizard_screen = 3
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# SCREEN 3: PORTFOLIO CHOICES
# ═══════════════════════════════════════════════════════════════════

elif screen == 3:
    st.title("🎯 Your Portfolio Choices")
    
    st.markdown("## Choose one of three simple approaches:")
    
    st.markdown("---")
    
    option = st.radio(
        "Select your preferred option:",
        [
            "1️⃣ Easy Mode (1 ETF) - For beginners",
            "2️⃣ Balanced Portfolio (3 ETFs) - Growth + Safety",
            "3️⃣ All-Weather Portfolio (5 ETFs) - Most stable long-term",
            "4️⃣ Fully Optimized Portfolio - AI-powered best mix"
        ],
        index=2  # Default to All-Weather
    )
    
    st.markdown("---")
    
    # Show details based on selection
    if "Easy Mode" in option:
        st.success("""
        **Easy Mode: Just SPY**
        
        - One ETF that tracks the S&P 500
        - Simplest option for beginners
        - Buy the same amount every month
        - Long-term: ~10% per year average
        """)
    
    elif "Balanced" in option:
        st.success("""
        **Balanced Portfolio: SPY + TLT + GLD**
        
        - **SPY:** US stocks (growth)
        - **TLT:** US bonds (safety)
        - **GLD:** Gold (inflation protection)
        
        Mix of growth + safety for most people.
        """)
    
    elif "All-Weather" in option:
        st.success("""
        **All-Weather Portfolio: 5 ETFs** ⭐ RECOMMENDED
        
        - **SPY:** US stocks (30%)
        - **TLT:** Long-term bonds (30%)
        - **GLD:** Gold (20%)
        - **IEF:** Mid-term bonds (10%)
        - **UUP:** US Dollar (10%)
        
        Built to survive crashes, inflation, and recessions.
        **Most stable long-term option.**
        """)
    
    else:  # Fully Optimized
        st.success("""
        **Fully Optimized Portfolio**
        
        Meridian uses advanced AI + analytics to compute the best ETF mix.
        
        - Tests 1000s of combinations
        - Optimizes for your goals
        - Balances risk and return
        - Updates monthly
        """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back"):
            st.session_state.wizard_screen = 2
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.wizard_screen = 4
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# SCREEN 4: HOW IT WORKS
# ═══════════════════════════════════════════════════════════════════

elif screen == 4:
    st.title("⚡ How It Works")
    
    st.markdown("## Just 3 simple steps:")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1️⃣ Pick")
        st.markdown("Choose a portfolio from the options")
        st.image("https://via.placeholder.com/150x150/4CAF50/FFFFFF?text=Pick", width=150)
    
    with col2:
        st.markdown("### 2️⃣ Optimize")
        st.markdown("Click the Optimize button")
        st.image("https://via.placeholder.com/150x150/2196F3/FFFFFF?text=Optimize", width=150)
    
    with col3:
        st.markdown("### 3️⃣ Download")
        st.markdown("Get your investment plan (PDF)")
        st.image("https://via.placeholder.com/150x150/FF9800/FFFFFF?text=Download", width=150)
    
    st.markdown("---")
    
    st.info("""
    **💡 You can buy ETFs using:**
    - Revolut
    - Trading212
    - XTB
    - eToro
    - Interactive Brokers (IBKR)
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back"):
            st.session_state.wizard_screen = 3
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.wizard_screen = 5
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# SCREEN 5: MONTHLY ROUTINE
# ═══════════════════════════════════════════════════════════════════

elif screen == 5:
    st.title("📅 Monthly Routine")
    
    st.markdown("## Once per month, you will:")
    
    st.markdown("---")
    
    steps = [
        ("1️⃣", "Open Meridian", "Takes 5 seconds"),
        ("2️⃣", "Click 'Optimize Portfolio'", "Meridian updates your plan"),
        ("3️⃣", "Download your plan", "PDF with exact instructions"),
        ("4️⃣", "Buy ETFs on your broker", "Follow the plan exactly")
    ]
    
    for icon, step, description in steps:
        st.markdown(f"### {icon} {step}")
        st.caption(description)
        st.markdown("")
    
    st.markdown("---")
    
    st.success("✅ **That's it!** Simple monthly routine = long-term wealth.")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back"):
            st.session_state.wizard_screen = 4
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.wizard_screen = 6
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# SCREEN 6: READY!
# ═══════════════════════════════════════════════════════════════════

elif screen == 6:
    st.title("🎉 You're Ready!")
    
    st.markdown("## Your next action:")
    
    st.markdown("---")
    
    st.success("""
    ### 👉 Click "Portfolio Designer" in the sidebar
    
    **Start with:**
    - **All-Weather Portfolio** (recommended for most people)
    
    **Or explore:**
    - Strategy Evolution (advanced)
    - AI Research Agents (expert analysis)
    - RL Trainer (optimization)
    """)
    
    st.markdown("---")
    
    st.info("""
    💡 **Tips for success:**
    - Start small (invest only what you can afford to lose)
    - Be patient (good portfolios take years, not days)
    - Rebalance monthly (don't panic-sell during crashes)
    - Trust the system (Meridian uses proven mathematics)
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.wizard_screen = 5
            st.rerun()
    
    with col2:
        if st.button("🚀 Open Portfolio Designer", type="primary", use_container_width=True):
            mark_wizard_complete()
            st.success("✅ Wizard complete! Navigate using the sidebar →")
            st.balloons()
    
    with col3:
        if st.button("Exit Wizard"):
            mark_wizard_complete()
            st.info("Navigate using the sidebar →")

# Footer
st.markdown("---")
st.caption("Phase 9 | User Onboarding Wizard")
st.caption("🌟 Making institutional-grade quant research accessible to everyone")

