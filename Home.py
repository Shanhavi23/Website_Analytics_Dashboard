import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
# import query
import time
from streamlit_extras.metric_cards import style_metric_cards

st.set_option('deprecation.showPyplotGlobalUse', False)
import plotly.graph_objs as go

st.set_page_config(page_title="Website Analytics", page_icon="🌏", layout='wide')
st.header('ANALYTICAL PROCESSING, KPI, TRENDS & PREDICTIONS')
st.subheader('🌐 Insurance Descriptive Analytics')
st.markdown('##')

theme_plotly = None

# load Style css
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

custom_css = """
<style>
body {
    base="light";
    background-color: #1a4158; /* secondaryBackgroundColor */
    color: #00010a; /* textColor */
}
.sidebar .sidebar-content {
    background-color: #058f9e; /* primaryColor */
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# fetch data
# result = query.view_all_data()
# df = pd.DataFrame(result, columns=['Policy', 'Expiry', 'Location', 'State', 'Region', 'Investment', 'Construction','BusinessType', 'Earthquake', 'Flood', 'Rating', 'id'])
df = pd.read_csv("data.csv")
# st.dataframe(df)

# sidebar
st.sidebar.image("bird_2.jpg", caption='Online Analytics')

# switcher
st.sidebar.header('Please filter')
region = st.sidebar.multiselect(label='Select region', options=df['Region'].unique(), default=df['Region'].unique())
location = st.sidebar.multiselect(label='Select location', options=df['Location'].unique(),
                                  default=df['Location'].unique())
cons = st.sidebar.multiselect(label='Select Construction', options=df['Construction'].unique(),
                              default=df['Construction'].unique())

df_selection = df.query(
    'Region==@region & Location==@location & Construction==@cons'
)


# st.dataframe(df_selection)
def Home():
    with st.expander('Tabular'):
        showData = st.multiselect('Filter: ', df_selection.columns)
        st.write(df_selection[showData])
    # compute top analytics
    df_selection['Investment'] = pd.to_numeric(df_selection['Investment'], errors='coerce')
    total_investment = float(df_selection['Investment'].sum())
    investment_mode = float(df_selection['Investment'].mode())
    investment_mean = float(df_selection['Investment'].mean())
    investment_median = float(df_selection['Investment'].median())
    rating = float(df_selection['Rating'].sum())

    total1, total2, total3, total4, total5 = st.columns(5, gap='medium')
    with total1:
        st.info('Total Investment', icon='💰')
        st.metric(label='sum TZS', value='{:,.0f}'.format(total_investment))
    with total2:
        st.info('Most frequent', icon='💰')
        st.metric(label='mode TZS', value='{:,.0f}'.format(investment_mode))
    with total3:
        st.info('Average', icon='💰')
        st.metric(label='average TZS', value='{:,.0f}'.format(investment_mean))
    with total4:
        st.info('Central Earnings', icon='💰')
        st.metric(label='median TZS', value='{:,.0f}'.format(investment_median))
    with total5:
        st.info('Ratings', icon='💰')
        st.metric(label='Rating', value=numerize(rating), help='''Total Rating: {} '''.format(rating))
    style_metric_cards(background_color="15146A", border_left_color="#686664", border_color="#000000",
                       box_shadow="#F71938")
    with st.expander("DISTRIBUTIONS BY FREQUENCY"):
        df.hist(figsize=(16, 8), color='#898784', zorder=2, rwidth=0.9, legend=['Investment']);
        st.pyplot()


# graphs

def graphs():
    # total_investment = int(df_selection['Investment'].sum())
    # averageRating = int(round(df_selection['Rating']).mean(), 2)

    # simple bar graph
    investment_by_business_type = (
        df_selection.groupby(by=['BusinessType']).count()[['Investment']].sort_values(by='Investment')
    )
    fig_investment = px.bar(
        investment_by_business_type,
        x='Investment',
        y=investment_by_business_type.index,
        orientation='h',
        title='<b> Investment by Business Type </b>',
        color_discrete_sequence=['#0083b8'] * len(investment_by_business_type),
        template='plotly_white'
    )
    fig_investment.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=(dict(showgrid=False))
    )

    # simple line graph
    investment_state = (
        df_selection.groupby(by=['State']).count()[['Investment']]
    )
    fig_state = px.line(
        investment_state,
        y='Investment',
        x=investment_state.index,
        orientation='h',
        title='<b> Investment by State </b>',
        color_discrete_sequence=['#0083b8'] * len(investment_state),
        template='plotly_white'
    )
    fig_state.update_layout(
        xaxis=(dict(tickmode='linear')),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=(dict(showgrid=False))
    )

    left, right, center = st.columns(3)
    left.plotly_chart(fig_state, use_container_width=True)
    right.plotly_chart(fig_investment, use_container_width=True)

    with center:
        # pie chart
        fig = px.pie(df_selection, values='Rating', names='State', title='RATINGS BY REGIONS')
        fig.update_layout(legend_title="Regions", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)


def Progressbar():
    st.markdown("""<style>.stProgress>div>div>div>div{background-image:linear-gradient(to right,#99ff99,
    #FFFF00)}</style>""", unsafe_allow_html=True)
    target = 3000000000
    current = df_selection["Investment"].sum()
    percent = round((current / target * 100))
    my_bar = st.progress(0)

    if percent > 100:
        st.subheader('Target done !')
    else:
        st.write('You have ', percent, '%', 'of ', format(target, 'd'), 'TZS')
        for percent_complete in range(percent):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1, text='Target Percentage')


def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title='Main Menu',
            options=['Home', 'Progress'],
            icons=['house', 'eye'],
            menu_icon='cast',
            default_index=0,
            orientation='v'
        )
    if selected == 'Home':
        st.subheader(f'Page: {selected}')
        Home()
        graphs()
    if selected == 'Progress':
        st.subheader(f'Page: {selected}')
        Progressbar()
        graphs()


sideBar()

st.subheader('PICK FEATURES TO EXPLORE DISTRIBUTIONS TRENDS BY QUARTILES', )
# feature_x = st.selectbox('Select feature for x Qualitative data', df_selection.select_dtypes("object").columns)
feature_y = st.selectbox('Select feature for y Quantitative Data', df_selection.select_dtypes("number").columns)
fig2 = go.Figure(
    data=[go.Box(x=df['BusinessType'], y=df[feature_y])],
    layout=go.Layout(
        title=go.layout.Title(text="BUSINESS TYPE BY QUARTILES OF INVESTMENT"),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Set plot background color to transparent
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show x-axis grid and set its color
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show y-axis grid and set its color
        font=dict(color='#cecdcd'),  # Set text color to black
    )
)
# Display the Plotly figure using Streamlit
st.plotly_chart(fig2, use_container_width=True)

# theme
hide_st_style = '''
<style>
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}
</style>
'''
