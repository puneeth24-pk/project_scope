import streamlit as st
import requests

# Your Render backend URL
BACKEND_URL = "https://projscopebackend.onrender.com/projects/"

st.title("📚 Project Submission Portal")

# Sidebar navigation
menu = ["Submit Project", "View Projects"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------ Submit Project ------------------ #
if choice == "Submit Project":
    st.header("Submit a New Project")

    project_name = st.text_input("Project Name")
    idea = st.text_area("Project Idea")
    team_members = st.text_input("Team Members (comma separated)")
    roll_number = st.text_input("Roll Number")
    class_name = st.text_input("Class")
    year = st.number_input("Year", min_value=1, max_value=10, step=1)
    branch = st.text_input("Branch")
    sec = st.text_input("Section")
    tools = st.text_input("Tools")
    technologies = st.text_input("Technologies")

    if st.button("Submit"):
        data = {
            "project_name": project_name,
            "idea": idea,
            "team_members": team_members,
            "roll_number": roll_number,
            "class_name": class_name,
            "year": year,
            "branch": branch,
            "sec": sec,
            "tools": tools,
            "technologies": technologies
        }
        response = requests.post(BACKEND_URL, json=data)
        if response.status_code == 200:
            st.success("✅ Project submitted successfully!")
        else:
            st.error("❌ Error submitting project. Try again!")

# ------------------ View / Update / Delete Projects ------------------ #
elif choice == "View Projects":
    st.header("All Projects")

    response = requests.get(BACKEND_URL)
    if response.status_code == 200:
        projects = response.json()
        for proj in projects:
            st.subheader(f"{proj['project_name']} ({proj['roll_number']})")
            st.write(f"**Idea:** {proj['idea']}")
            st.write(f"**Team Members:** {proj['team_members']}")
            st.write(f"**Class:** {proj['class_name']} | **Year:** {proj['year']}")
            st.write(f"**Branch:** {proj['branch']} | **Section:** {proj['sec']}")
            st.write(f"**Tools:** {proj['tools']}")
            st.write(f"**Technologies:** {proj['technologies']}")

            col1, col2 = st.columns(2)

            # Delete button
            with col1:
                if st.button(f"Delete {proj['id']}"):
                    del_response = requests.delete(f"{BACKEND_URL}{proj['id']}")
                    if del_response.status_code == 200:
                        st.success("✅ Project deleted successfully!")
                    else:
                        st.error("❌ Error deleting project.")

            # Update button (simplified)
            with col2:
                if st.button(f"Update {proj['id']}"):
                    new_idea = st.text_area(f"New Idea for {proj['project_name']}")
                    if new_idea:
                        update_data = {"idea": new_idea}
                        put_response = requests.put(f"{BACKEND_URL}{proj['id']}", json=update_data)
                        if put_response.status_code == 200:
                            st.success("✅ Project updated successfully!")
                        else:
                            st.error("❌ Error updating project.")
    else:
        st.error("❌ Failed to fetch projects.")
