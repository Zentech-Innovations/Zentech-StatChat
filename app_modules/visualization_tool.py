import streamlit as st
import plotly.express as px
import pandas as pd
from google.genai.types import FunctionDeclaration, Schema, Tool, Type

def create_comparison_chart(data, title, chart_type='bar', x_axis='item', y_axis='value'):
    if not data or not all(x_axis in d and y_axis in d for d in data):
        st.warning("Chart could not be generated due to incomplete data from the AI.")
        return None
    
    df = pd.DataFrame(data)
    
    if chart_type.lower() == 'pie':
        fig = px.pie(df, names=x_axis, values=y_axis, title=title, hole=0.3)
        fig.update_traces(textinfo='percent+label', pull=[0.05] * len(df))
    
    elif chart_type.lower() == 'line':
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date')
        fig = px.line(df, x=x_axis, y=y_axis, title=title, markers=True, text=y_axis)
        fig.update_traces(textposition="top center")

    else: 
        fig = px.bar(df, x=x_axis, y=y_axis, title=title, text=y_axis, color=x_axis)
        fig.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
    
    fig.update_layout(
        title_x=0.5,
        yaxis_title=None,
        xaxis_title=None,
        legend_title=None,
        showlegend=(chart_type.lower() != 'line') 
    )
    st.session_state.figure_to_display = fig
    return f"Success: The chart titled '{title}' has been generated and is ready for display."

# For Gemini
VISUALIZATION_TOOL_GEMINI = FunctionDeclaration(
    name="display_comparison_chart",
    description="Displays a bar or pie chart to visually compare financial data, such as profits/losses across different stocks or segments.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "chart_type": Schema(type=Type.STRING, description="The type of chart. Either 'bar' or 'pie'."),
            "title": Schema(type=Type.STRING, description="The title for the chart."),
            "data": Schema(
                type=Type.ARRAY,
                description="The data to plot. A list of objects, where each object is a data point.",
                items=Schema(
                    type=Type.OBJECT,
                    properties={
                        "item": Schema(type=Type.STRING, description="The label for the data point (e.g., stock or segment name)."),
                        "value": Schema(type=Type.NUMBER, description="The numerical value for the data point (e.g., profit amount).")
                    },
                    required=["item", "value"]
                )
            )
        },
        required=["title", "data", "chart_type"]
    )
)

# For OpenAI
VISUALIZATION_TOOL_OPENAI = {
    "type": "function",
    "function": {
        "name": "display_comparison_chart",
        "description": "Displays a bar, pie, or line chart to visually compare financial data.",
        "parameters": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["bar", "pie", "line"],
                    "description": "The type of chart to display."
                },
                "title": {"type": "string", "description": "The title for the chart."},
                "data": {
                    "type": "array",
                    "description": "The data to be plotted. A list of objects, where each object is a data point.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item": {"type": "string", "description": "The label for a data point (e.g., stock name)."},
                            "value": {"type": "number", "description": "The numerical value for a data point (e.g., profit amount)."},
                            "Date": {"type": "string", "description": "The date for a data point (used for line charts)."}
                        },
                    }
                },
                "x_axis": {"type": "string", "description": "The key from the data object to use for the x-axis."},
                "y_axis": {"type": "string", "description": "The key from the data object to use for the y-axis."}
            },
            "required": ["title", "data", "chart_type", "x_axis", "y_axis"]
        }
    }
}

