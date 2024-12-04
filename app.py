import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def secret_santa_draw(participants):
    names = list(participants.keys())
    assignments = {}
    random.shuffle(names)
    
    for i, giver in enumerate(names):
        potential_receivers = [name for name in names if name != giver and name not in assignments.values()]
        if not potential_receivers:
            return secret_santa_draw(participants)
        receiver = random.choice(potential_receivers)
        assignments[giver] = receiver
    return assignments

def send_email(sender_email, sender_password, recipient_email, giver_name, receiver_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Your Secret Santa Assignment! 🎅"

        body = f"""
        Hi {giver_name}!
        
        You are the Secret Santa for: {receiver_name}
        
        Happy gifting! 🎁
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def main():
    st.title("🎅 Secret Santa Generator 🎁")

    # Initialize session state for participants
    if 'participants' not in st.session_state:
        st.session_state.participants = []

    # Dynamic participant input fields
    st.subheader("Add Participants")

    # Add new participant inputs
    col1, col2, col3 = st.columns([2,2,.2])
    with col1:
        new_name = st.text_input("", key="new_name", placeholder="Enter name")
    with col2:
        new_email = st.text_input("", key="new_email", placeholder="Enter email")
    with col3:
        def add_participant():
            if new_name and new_email:
                st.session_state.participants.append({
                    'name': new_name,
                    'email': new_email
                })
                # Reset inputs
                st.session_state.new_name = ""
                st.session_state.new_email = ""
            else:
                st.error("Please enter both name and email!")

        st.button("➕", key="add_button", on_click=add_participant)

    # Display current participants with remove buttons
    if st.session_state.participants:
        st.subheader("Current Participants")
        for idx, participant in enumerate(st.session_state.participants):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(participant['name'])
            with col2:
                st.text(participant['email'])
            with col3:
                def remove_participant(index=idx):
                    st.session_state.participants.pop(index)

                st.button("❌", key=f"remove_{idx}", on_click=remove_participant)

    # Generate Secret Santa assignments and send emails
    if len(st.session_state.participants) >= 3:
        st.subheader("Generate Secret Santa Assignments")
        
        # Wrap in a form
        with st.form("generate_form"):
            submit_button = st.form_submit_button("Generate and Send Assignments")
            
            if submit_button:
                participants_dict = {p['name']: p['email'] for p in st.session_state.participants}
                assignments = secret_santa_draw(participants_dict)

                success_count = 0
                for giver, receiver in assignments.items():
                    if send_email(
                        st.secrets['EMAIL'],
                        st.secrets['PASSWORD'],
                        participants_dict[giver],
                        giver,
                        receiver
                    ):
                        success_count += 1

                if success_count == len(assignments):
                    st.success("All Secret Santa assignments have been sent successfully! 🎄")
                    st.session_state.participants = []  # Clear participants after assignments
                else:
                    st.error("Some emails failed to send. Please check the configuration and try again.")

                # Clear everything and refresh the display
                st.session_state.participants = []
                st.rerun()

if __name__ == "__main__":
    main()
