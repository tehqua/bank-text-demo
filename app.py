import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.etl.loader import load_and_validate
from src.etl.preprocessor import preprocess_dataframe
from src.models.topic.auto_topic import AutoTopicModel
from src.models.sentiment.classifier import SentimentClassifier
from src.models.sentiment.fallback import fallback_predict
from src.models.trainer import train_sentiment_model, train_topic_supervised_model, train_topic_auto_model
from src.viz.wordcloud import generate_wordcloud
from src.viz.bubble_chart import create_bubble_chart, create_sentiment_distribution_chart
from src.viz.table_view import create_topic_summary_table, create_sentiment_summary_table, filter_dataframe
from src.agents.goal_manager import GoalManager
from src.agents.monitor import Monitor
from src.agents.planner import Planner
from src.agents.executor import Executor
from src.agents.memory import Memory
from src.agents.coordinator import MultiAgentCoordinator
from config.settings import TOPIC_MODEL_DIR, SENTIMENT_MODEL_DIR, RAW_DIR
from src.utils.export import export_to_csv
from src.chatbot.agent import ChatbotAgent

st.set_page_config(page_title="Bank Text Analysis", layout="wide")

if 'df_pandas' not in st.session_state:
    st.session_state.df_pandas = None

if 'chatbot_agent' not in st.session_state:
    st.session_state.chatbot_agent = None

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'coordinator' not in st.session_state:
    st.session_state.coordinator = None

st.title("Bank Text Analysis Demo")
st.markdown("Upload CSV, analyze topics & sentiment, visualize results")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Upload & Analyze", "Visualizations", "Edit & Export", "Training", "Agentic AI", "💬 AI Chatbot"])

with tab1:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])

    if uploaded_file:
        file_path = RAW_DIR / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File uploaded: {uploaded_file.name}")

        if st.button("Run Analysis"):
            with st.spinner("Processing..."):
                df = load_and_validate(str(file_path))
                df = preprocess_dataframe(df)

                texts = df['comment_lower'].tolist()

                topic_auto_path = TOPIC_MODEL_DIR / "topic_auto"
                if topic_auto_path.exists():
                    topic_model = AutoTopicModel.load(topic_auto_path)
                    topic_labels, _ = topic_model.predict(texts)
                else:
                    st.warning("No topic model found, training auto topic model")
                    topic_model = train_topic_auto_model(texts, n_clusters=8, model_name="topic_auto", log_mlflow=False)
                    topic_labels, _ = topic_model.predict(texts)

                sentiment_path = SENTIMENT_MODEL_DIR / "sentiment_model"
                if sentiment_path.exists():
                    sentiment_model = SentimentClassifier.load(sentiment_path)
                    sentiment_labels, sentiment_scores, _ = sentiment_model.predict_with_scores(texts)
                else:
                    st.warning("No sentiment model found, using fallback")
                    sentiment_labels, sentiment_scores = fallback_predict(texts)

                df['topic_label'] = topic_labels
                df['sentiment_label'] = sentiment_labels
                df['sentiment_score'] = sentiment_scores

                st.session_state.df_pandas = df

                st.success("Analysis complete!")
                st.dataframe(df[['comment', 'topic_label', 'sentiment_label', 'sentiment_score']].head(20))

with tab2:
    st.header("Visualizations")

    if st.session_state.df_pandas is not None:
        df_pandas = st.session_state.df_pandas

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sentiment Distribution")
            sentiment_counts = df_pandas['sentiment_label'].value_counts().to_dict()
            fig_sentiment = create_sentiment_distribution_chart(sentiment_counts)
            st.plotly_chart(fig_sentiment, use_container_width=True)

        with col2:
            st.subheader("Topic Summary")
            topic_summary = create_topic_summary_table(df_pandas)
            st.dataframe(topic_summary, use_container_width=True)

        st.subheader("Topic Bubble Chart")
        topic_stats = df_pandas.groupby('topic_label').agg({
            'comment': 'count',
            'sentiment_score': 'mean'
        }).reset_index()
        topic_stats.columns = ['topic_label', 'count', 'avg_sentiment']
        fig_bubble = create_bubble_chart(topic_stats)
        st.plotly_chart(fig_bubble, use_container_width=True)

        st.subheader("Word Cloud")
        selected_topic = st.selectbox("Select topic", ["All"] + list(df_pandas['topic_label'].unique()))

        if selected_topic == "All":
            texts_for_wc = df_pandas['comment_lower'].tolist()
        else:
            texts_for_wc = df_pandas[df_pandas['topic_label'] == selected_topic]['comment_lower'].tolist()

        fig_wc = generate_wordcloud(texts_for_wc, selected_topic)
        if fig_wc:
            st.pyplot(fig_wc)
        else:
            st.warning("Not enough text for word cloud")

    else:
        st.info("Upload and analyze data first")

with tab3:
    st.header("Edit & Export")

    if st.session_state.df_pandas is not None:
        df_pandas = st.session_state.df_pandas

        st.subheader("Filter Data")
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_topic = st.selectbox("Filter by topic", ["All"] + list(df_pandas['topic_label'].unique()))

        with col2:
            filter_sentiment = st.selectbox("Filter by sentiment", ["All"] + list(df_pandas['sentiment_label'].unique()))

        with col3:
            if 'source' in df_pandas.columns:
                filter_source = st.selectbox("Filter by source", ["All"] + list(df_pandas['source'].unique()))
            else:
                filter_source = "All"

        filtered_df = filter_dataframe(df_pandas, filter_topic, filter_sentiment, filter_source)

        st.dataframe(filtered_df[['comment', 'topic_label', 'sentiment_label', 'sentiment_score']], use_container_width=True)

        st.subheader("Export")
        if st.button("Export to CSV"):
            export_path = RAW_DIR / "export_result.csv"
            filtered_df.to_csv(export_path, index=False, encoding='utf-8-sig')
            st.success(f"Exported to {export_path}")
            st.download_button("Download CSV", data=open(export_path, 'rb'), file_name="export_result.csv")

    else:
        st.info("Upload and analyze data first")

with tab4:
    st.header("Model Training")

    use_mlflow = st.checkbox("Enable MLflow Tracking", value=True)
    if use_mlflow:
        st.info("MLflow tracking enabled - experiments will be logged to mlruns/")

    with st.expander("🗑️ Clean Models (Force Retrain)"):
        st.warning("⚠️ This will delete all trained models. You will need to retrain.")
        col1, col2, col3 = st.columns(3)

        if col1.button("Clean Topic Models"):
            import shutil
            topic_auto_path = TOPIC_MODEL_DIR / "topic_auto"
            if topic_auto_path.exists():
                shutil.rmtree(topic_auto_path)
                st.success("Topic models cleaned!")
            else:
                st.info("No topic models found")

        if col2.button("Clean Sentiment Models"):
            import shutil
            sentiment_path = SENTIMENT_MODEL_DIR / "sentiment_model"
            if sentiment_path.exists():
                shutil.rmtree(sentiment_path)
                st.success("Sentiment models cleaned!")
            else:
                st.info("No sentiment models found")

        if col3.button("Clean All Models"):
            import shutil
            for path in [TOPIC_MODEL_DIR / "topic_auto", SENTIMENT_MODEL_DIR / "sentiment_model"]:
                if path.exists():
                    shutil.rmtree(path)
            st.success("All models cleaned!")

    st.subheader("Train Sentiment Model")
    sentiment_train_file = st.file_uploader("Upload labeled sentiment CSV (comment, sentiment_label)", type=['csv'], key="sentiment")

    if sentiment_train_file:
        if st.button("Train Sentiment Model"):
            with st.spinner("Training sentiment model..."):
                train_df = pd.read_csv(sentiment_train_file)
                if 'comment' in train_df.columns and 'sentiment_label' in train_df.columns:
                    texts = train_df['comment'].fillna("").tolist()
                    labels = train_df['sentiment_label'].tolist()

                    model, metrics = train_sentiment_model(texts, labels, log_mlflow=use_mlflow)

                    st.success(f"✅ Sentiment model trained!")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Accuracy", f"{metrics.get('accuracy', 0):.3f}")
                    col2.metric("F1 (Macro)", f"{metrics.get('f1_macro', 0):.3f}")
                    col3.metric("F1 (Weighted)", f"{metrics.get('f1_weighted', 0):.3f}")

                    if use_mlflow:
                        st.info("📊 Check MLflow UI: run `mlflow ui` and visit http://localhost:5000")
                else:
                    st.error("CSV must have 'comment' and 'sentiment_label' columns")

    st.subheader("Train Topic Model")
    topic_train_file = st.file_uploader("Upload labeled topic CSV (comment, topic_label)", type=['csv'], key="topic")

    if topic_train_file:
        if st.button("Train Topic Model"):
            with st.spinner("Training topic model..."):
                train_df = pd.read_csv(topic_train_file)
                if 'comment' in train_df.columns and 'topic_label' in train_df.columns:
                    texts = train_df['comment'].fillna("").tolist()
                    labels = train_df['topic_label'].tolist()

                    model, metrics = train_topic_supervised_model(texts, labels, log_mlflow=use_mlflow)

                    st.success(f"✅ Topic model trained!")
                    col1, col2 = st.columns(2)
                    col1.metric("Accuracy", f"{metrics.get('accuracy', 0):.3f}")
                    col2.metric("F1 (Macro)", f"{metrics.get('f1_macro', 0):.3f}")

                    if use_mlflow:
                        st.info("📊 Check MLflow UI: run `mlflow ui` and visit http://localhost:5000")
                else:
                    st.error("CSV must have 'comment' and 'topic_label' columns")

with tab5:
    st.header("🤖 True Agentic AI - Multi-Agent System")
    st.markdown("**Autonomous agents with continuous learning and inter-agent communication**")

    if st.session_state.df_pandas is not None:
        df_pandas = st.session_state.df_pandas

        if st.session_state.coordinator is None:
            st.session_state.coordinator = MultiAgentCoordinator()
            st.success("✅ Multi-Agent System initialized with 7 agents")

        coordinator = st.session_state.coordinator

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚀 Autonomous Actions")

            if st.button("Run Full Agentic Workflow", use_container_width=True):
                with st.spinner("Running autonomous multi-agent workflow..."):
                    results = coordinator.run_full_agentic_workflow(df_pandas)

                    st.success(f"✅ Workflow completed: {results['status']}")

                    for step in results['steps']:
                        if step['status'] == 'success':
                            st.info(f"✓ {step['step']}")
                        else:
                            st.warning(f"⚠ {step['step']}: {step.get('status')}")

            if st.button("Trigger Continuous Improvement", use_container_width=True):
                with st.spinner("Triggering continuous learning cycle..."):
                    results = coordinator.trigger_continuous_improvement(df_pandas)

                    st.success("✅ Continuous improvement triggered")
                    st.json(results)

        with col2:
            st.subheader("📊 System Status")

            if st.button("Get System Status", use_container_width=True):
                status = coordinator.get_system_status()

                st.metric("Active Agents", status['coordinator']['agents_count'])
                st.metric("Model Cards", status['agents']['model_cards']['total_models'])
                st.metric("Total Goals", status['agents']['goals']['total_goals'])

                with st.expander("📈 Learning Status"):
                    learning = status['agents']['learning']
                    st.write(f"**Last Cycle:** {learning.get('last_cycle', 'N/A')}")
                    st.write(f"**Next Cycle:** {learning.get('next_cycle_in', 'N/A')}")
                    st.write(f"**Recent Improvements:**")
                    for imp in learning.get('recent_improvements', []):
                        st.write(f"  - {imp.get('model_type')}: {imp.get('improvement', 0):+.3f}")

        st.markdown("---")

        st.subheader("📡 Agent Communications")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("View Agent Messages"):
                messages = coordinator.get_agent_communications(limit=15)

                st.markdown("**Recent Inter-Agent Messages:**")
                for msg in messages[-10:]:
                    st.text(f"[{msg['priority']}] {msg['sender']} → {msg['topic']}")

        with col2:
            if st.button("View Coordination History"):
                history = coordinator.get_coordination_history(limit=10)

                st.markdown("**Recent Coordination Actions:**")
                for event in history:
                    st.text(f"{event.get('action')} at {event.get('timestamp')}")

        st.markdown("---")

        st.subheader("🎯 Model Cards & Performance")

        if st.button("View All Model Cards"):
            model_card_agent = coordinator.model_card_agent
            summary = model_card_agent.get_performance_summary()

            st.metric("Total Models", summary['total_models'])

            if summary['models']:
                st.markdown("**Model Performance:**")
                for model_info in summary['models']:
                    with st.expander(f"📦 {model_info['model_name']} ({model_info['model_type']})"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Accuracy", f"{model_info['accuracy']:.3f}")
                        col2.metric("F1 Score", f"{model_info['f1_score']:.3f}")
                        col3.metric("Status", model_info['status'])
            else:
                st.info("No model cards yet. Train a model to create model cards automatically.")

    else:
        st.info("📁 Upload and analyze data first to activate the Multi-Agent System")

with tab6:
    st.header("💬 AI Chatbot Assistant")

    st.markdown("""
    **Chatbot này có thể giúp bạn:**
    - Truy vấn và phân tích data comments
    - Xem thống kê tổng quan
    - Tìm top issues tiêu cực
    - Kiểm tra anomalies
    - Quản lý models (xóa để retrain)

    **Powered by:** Ollama (Local LLM - Free)
    """)

    if st.session_state.chatbot_agent is None:
        st.session_state.chatbot_agent = ChatbotAgent(st.session_state.df_pandas)
    else:
        st.session_state.chatbot_agent.update_data(st.session_state.df_pandas)

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
            st.session_state.chatbot_agent.clear_history()
            st.rerun()

        st.markdown("---")
        st.markdown("**Ví dụ câu hỏi:**")
        st.markdown("- Cho tôi thống kê tổng quan")
        st.markdown("- Top 5 vấn đề tiêu cực là gì?")
        st.markdown("- Kiểm tra anomalies")
        st.markdown("- Có bao nhiêu comment về chuyển tiền?")

    with col1:
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Hỏi AI Assistant...")

        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("AI đang suy nghĩ..."):
                    response = st.session_state.chatbot_agent.chat(user_input)
                    st.markdown(response)

            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
