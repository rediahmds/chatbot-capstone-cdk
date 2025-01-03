"""
chatbot_app.py
this module is a streamlit-based chatbot app called TemanTenang, 
providing an easy-to-use chat interface 
with conversational AI with knowledge around mental health.

some of the features available:
- Predefined and custom persona options for chatbot behavior
- temperature slider to adjust AI model response
- Integration with ConversationManager for managing conversation logic
- User interface with chat input and conversation history display

Dependencies:
- streamlit: for building user interface
- ConversationManager: for handling the conversation
- DEFAULT_TEMPERATURE: for configuring the default temperature value.

Usage:
1. Create an instance of the Chatbot class.
2. Call the `generate_ui` method to launch the interface.

Translated with DeepL.com (free version)
"""
import streamlit as st
from services.conversation_manager import ConversationManager
from util.get_instance_id import get_instance_id
from config.settings import DEFAULT_TEMPERATURE


class Chatbot:
    def __init__(self, page_title="TemanTenang | Tim 7 CendekiAwan"):
        self.instance_id = get_instance_id()
        self.page_title = page_title

        if "chat_manager" not in st.session_state:
            st.session_state["chat_manager"] = ConversationManager()

        self.chat_manager = st.session_state["chat_manager"]

        if "conversation_history" not in st.session_state:
            st.session_state["conversation_history"] = (
                self.chat_manager.conversation_history
            )

        self.conversation_history = st.session_state["conversation_history"]

    def generate_ui(self):
        st.set_page_config(page_title=self.page_title, page_icon="❤️")
        st.title("TemanTenang")
        st.write(f"**EC2 Instance ID**: {self.instance_id}")
        self._display_sidebar()
        user_input = st.chat_input("Write a message")
        if user_input:
            self._display_conversation_history(user_input)
        else:
            self._display_conversation_history()

    def _display_user_input(self, user_input: str):
        with st.chat_message("user"):
            st.write(user_input)

    def _display_assistant_response(self, user_input):
        temperature = st.session_state.get("temperature", DEFAULT_TEMPERATURE)
        response_stream = self.chat_manager.chat_completion(
            prompt=user_input, stream=True, temperature=temperature
        )
        with st.chat_message("assistant"):
            streamed_response = st.write_stream(response_stream)

        self.conversation_history.append(
            {"role": "assistant", "content": streamed_response}
        )

    def _display_conversation_history(self, user_input: str = None):
        for message in self.conversation_history:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        if user_input:
            self._display_user_input(user_input)
            self._display_assistant_response(user_input)

    def _display_sidebar(self):
        with st.sidebar:
            toggle_custom_persona = st.toggle("Use custom persona", value=False)
            persona = self._display_persona_option(disabled=toggle_custom_persona)
            self._handle_persona_changes(
                persona=persona, toggle_custom_persona=toggle_custom_persona
            )

            temperature = st.slider(
                "Set Temperature",
                min_value=0.0,
                max_value=1.0,
                value=DEFAULT_TEMPERATURE,
                step=0.01,
                help="Adjusment randomness of chatbot response."
            )

            st.session_state["temperature"] = temperature

    def _display_persona_option(self, disabled=False):
        personalities = ("Professional", "Empathetic", "Motivational")
        return st.selectbox("Select personality", personalities, disabled=disabled)

    def _handle_persona_changes(
        self, persona="Professional", toggle_custom_persona=False
    ):
        if toggle_custom_persona:
            custom_persona = st.text_area(
                "Define your own persona for the chatbot",
                placeholder="e.g. You are a software engineer who love to help others",
            )
            self._set_user_defined_persona(custom_persona)
        else:
            self._set_predefined_persona(persona)

    def _set_user_defined_persona(self, user_prompt: str):
        save_custom_persona = st.button(
            "Save", icon=":material/save:", use_container_width=True
        )
        if user_prompt and save_custom_persona:
            self._handle_custom_persona(user_prompt)

    def _handle_custom_persona(self, user_prompt: str):
        custom_persona = user_prompt
        self.chat_manager.set_system_persona(custom_persona)

    def _set_predefined_persona(self, persona="Professional"):
        persona_prompt = f"""The user has selected {persona} persona.
            Respond accordingly throughout this conversation."""
        system_message_with_chosen_persona = (
            self.chat_manager.system_message + persona_prompt
        )

        self.chat_manager.set_system_persona(system_message_with_chosen_persona)
