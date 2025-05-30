import streamlit as st
from dataLoading import load_wallet_data, extract_wallet_features, classify_wallet
import pandas as pd
import plotly.express as px
from test import WalletPersonaGenerator  # Use the renamed file

st.set_page_config(page_title="Onchain Wallet Persona Generator", layout="wide")
st.title("🦄 Onchain Wallet Persona Generator")
st.markdown(
    """
    Enter a wallet address to generate a detailed AI-powered persona profile, risk assessment, activity timeline, and personalized recommendations based on onchain data.
    """
)

wallet_address = st.text_input("Wallet Address", placeholder="0x...")

# Remove hf_token input and always use the fixed token
HF_TOKEN = "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"

generate_ai = st.checkbox("Generate AI-powered persona (uses HuggingFace model, may take time)", value=True)

if st.button("Generate Persona"):
    if not wallet_address or not wallet_address.startswith("0x") or len(wallet_address) < 10:
        st.error("Please enter a valid wallet address.")
    else:
        with st.spinner("Analyzing wallet and generating persona..."):
            data_dict = load_wallet_data()
            features = extract_wallet_features(wallet_address, data_dict)
            if features:
                features['classifications'] = classify_wallet(features)
                # Persona summary
                st.subheader("Persona Profile")
                st.markdown(f"**Social Handle:** `{features.get('social_handle', 'N/A')}`")
                st.markdown(f"**Classifications:** {', '.join(features.get('classifications', []))}")
                st.markdown(f"**Persona Profile:**\n\n{features.get('persona_profile', 'N/A')}")

                # AI Persona (HuggingFace model)
                if generate_ai:
                    with st.spinner("Generating AI persona with HuggingFace model (Mistral)..."):
                        try:
                            generator = WalletPersonaGenerator(hf_token=HF_TOKEN)
                            ai_persona_md = generator.generate_persona(features, detailed=True)
                            st.subheader("AI-Generated Persona (Mistral Model)")
                            st.markdown(ai_persona_md)
                        except Exception as e:
                            st.error(f"AI persona generation failed: {e}")

                # Scores
                st.subheader("Scores & Risk Assessment")
                col1, col2, col3 = st.columns(3)
                col1.metric("Wallet Health Score", features.get('wallet_health_score', 0), "0-100")
                col2.metric("Risk Score", features.get('risk_score', 0), "0-100 (higher = riskier)")
                col3.metric("Activity Score", features.get('activity_score', 0))

                # Portfolio
                st.subheader("Portfolio Overview")
                st.markdown(f"**Total Networth:** ${features.get('total_networth', 0):,.2f}")
                st.markdown(f"**Token Count:** {features.get('token_count', 0)}")
                st.markdown(f"**Top Tokens:** {', '.join(features.get('top_tokens', []))}")
                st.markdown(f"**DeFi Protocols:** {features.get('defi_protocols', 0)}")
                st.markdown(f"**Total DeFi USD:** ${features.get('total_defi_usd', 0):,.2f}")
                st.markdown(f"**NFT Collections:** {features.get('unique_nft_collections', 0)}")

                # --- Visualizations ---
                st.subheader("Visualizations")
                # Top Tokens Bar Chart
                token_df = data_dict.get("tokens", pd.DataFrame())
                if not token_df.empty and "wallet" in token_df.columns and "token_symbol" in token_df.columns and "usd_value" in token_df.columns:
                    user_tokens = token_df[token_df["wallet"] == wallet_address]
                    top_tokens = user_tokens.groupby("token_symbol")["usd_value"].sum().sort_values(ascending=False).head(10)
                    if not top_tokens.empty:
                        fig = px.bar(x=top_tokens.index, y=top_tokens.values, labels={"x": "Token", "y": "USD Value"}, title="Top 10 Tokens by USD Value")
                        st.plotly_chart(fig, use_container_width=True)

                # Portfolio Pie Chart (Tokens vs DeFi vs NFTs)
                pie_labels = []
                pie_values = []
                if features.get("total_networth", 0) > 0:
                    pie_labels.append("Tokens")
                    pie_values.append(features.get("token_balance_usd", 0))
                    pie_labels.append("DeFi")
                    pie_values.append(features.get("total_defi_usd", 0))
                    pie_labels.append("NFTs")
                    # For NFTs, estimate as a count (or set to 0 if not available)
                    pie_values.append(features.get("unique_nft_collections", 0) * 100)  # Arbitrary value for visualization
                    fig2 = px.pie(values=pie_values, names=pie_labels, title="Portfolio Allocation (USD, NFTs estimated)")
                    st.plotly_chart(fig2, use_container_width=True)

                # Activity Timeline (if available)
                stats_df = data_dict.get("stats", pd.DataFrame())
                if not stats_df.empty and "wallet" in stats_df.columns and "transactions_total" in stats_df.columns:
                    user_stats = stats_df[stats_df["wallet"] == wallet_address]
                    if not user_stats.empty and "transactions_total" in user_stats.columns:
                        st.markdown("**Activity Timeline (Total Transactions)**")
                        st.line_chart(user_stats[["transactions_total"]].rename(columns={"transactions_total": "Transactions"}))

                # Recommendations
                st.subheader("Personalized Recommendations")
                for rec in features.get('recommendations', []):
                    st.write(f"- {rec}")

                # Raw JSON (collapsible)
                with st.expander("Show Raw Persona JSON"):
                    st.json(features)
            else:
                st.error("No data found for this wallet or failed to generate persona.")
