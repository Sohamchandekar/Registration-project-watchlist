from operator import index

import pandas as pd
import re


def dataframeSafai(csv_file):
    df = pd.read_csv(csv_file)
    columns_to_drop = [
        'certificate_preview', 'extension_preview', 'appeal_status',
        'correction_status', 'extension_status', 'additional_data',
        'complain_against_status', 'Unnamed: 0', 'application_status',
        'payment_status'
    ]
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')

    def format_scrutiny_status(status):
        if isinstance(status, str):
            if "In Process More Information Required" in status:
                desk_match = re.search(r"Desk -(\d+)", status)
                desk_number = desk_match.group(1) if desk_match else ""
                return f"In Process (Desk {desk_number} Comment)"
            else:
                return status
        return status

    def shorten_and_wrap_comment(comment):
        if isinstance(comment, str):
            short_preview = comment[:100].replace('\n', ' ') + "..." if len(comment) > 100 else comment
            return f'''
            <div class="comment-preview" ondblclick="expandComment(this)">
                <span class="short">{short_preview}</span>
                <span class="full" style="display:none;">{comment}</span>
            </div>
            '''
        return comment

    if 'scrutiny_status' in df.columns:
        df['scrutiny_status'] = df['scrutiny_status'].apply(format_scrutiny_status)

    if 'comments' in df.columns:
        df['comments'] = df['comments'].apply(shorten_and_wrap_comment)

    return df

def style_dataframe(df):
    # Apply custom colors based on status
    def apply_status_colors(val):
        color = ''
        if isinstance(val, str):
            if "pending" in val.lower():
                color = 'red'
            elif "done" in val.lower():
                color = 'green'
            elif "in process" in val.lower():
                color = 'orange'
        return f'color: {color}; font-weight: bold' if color else 'font-weight: bold'

    # Apply color based on conditions for specific columns
    styled_df = df.style.applymap(apply_status_colors, subset=['scrutiny_status'])

    styled_df = styled_df.set_table_styles([
        # Header style
        {'selector': 'thead th',
         'props': [
             ('background-color', '#343a40'),  # dark grey
             ('color', 'white'),
             ('text-align', 'center'),
             ('font-size', '22px'),
             ('font-family', 'Segoe UI, sans-serif'),
             ('font-weight', '600'),
             ('padding', '12px')
         ]},

        # Cell style
        {'selector': 'tbody td',
         'props': [
             ('text-align', 'center'),
             ('font-family', 'Segoe UI, sans-serif'),
             ('border', '1px solid #dee2e6'),
             ('font-size', '20px'),
             ('padding', '10px')
         ]},

        # Table border and spacing
        {'selector': 'table',
         'props': [
             ('border-collapse', 'collapse'),
             ('width', '100%'),
             ('margin', 'auto'),
             ('box-shadow', '0px 4px 8px rgba(0, 0, 0, 0.1)')
         ]}
    ])

    # Alternating row colors
    styled_df = styled_df.set_properties(
        subset=pd.IndexSlice[::2, :], **{'background-color': '#f8f9fa'}  # light grey
    ).set_properties(
        subset=pd.IndexSlice[1::2, :], **{'background-color': '#ffffff'}  # white
    )

    return styled_df