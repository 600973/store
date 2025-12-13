from charts.base_chart import BaseChart
import json


class ChartRevenueDynamics(BaseChart):
    def __init__(self, chart_id='chart_revenue_dynamics', **kwargs):
        # Enable table and prompt tabs
        kwargs.setdefault('show_table', True)
        kwargs.setdefault('show_prompt', True)
        super().__init__(chart_id=chart_id, **kwargs)

    def get_js_code(self):
        # Получаем JS код для таблиц и промптов из базового класса
        table_js = self._generate_table_js()

        return f"""
        function update{self.chart_id}() {{
            const data = window.filteredData || window.rawData;

            const monthlyData = {{}};

            data.forEach(row => {{
                const year = row['Год'];
                const month = row['Месяц'];
                const store = row['Магазин'];
                const revenue = row['Выручка'];

                const dateKey = `${{year}}-${{String(month).padStart(2, '0')}}`;

                if (!monthlyData[dateKey]) {{
                    monthlyData[dateKey] = {{}};
                }}

                if (!monthlyData[dateKey][store]) {{
                    monthlyData[dateKey][store] = 0;
                }}

                monthlyData[dateKey][store] += revenue;
            }});

            const dates = Object.keys(monthlyData).sort();
            const stores = [...new Set(data.map(r => r['Магазин']))].sort((a, b) => {{
                const numA = parseInt(a.match(/\\d+/));
                const numB = parseInt(b.match(/\\d+/));
                return numA - numB;
            }});

            const traces = stores.map(store => {{
                return {{
                    x: dates,
                    y: dates.map(date => monthlyData[date][store] || 0),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: store,
                    hovertemplate: '<b>%{{fullData.name}}</b><br>Дата: %{{x}}<br>Выручка: %{{y:,.0f}} руб<extra></extra>'
                }};
            }});

            const layout = {{
                title: 'Динамика выручки по магазинам',
                xaxis: {{
                    title: 'Период',
                    type: 'category'
                }},
                yaxis: {{
                    title: 'Выручка (руб)',
                    tickformat: ',.0f'
                }},
                hovermode: 'closest',
                showlegend: true,
                legend: {{
                    orientation: 'v',
                    x: 1.02,
                    y: 1,
                    bgcolor: 'rgba(255,255,255,0.8)'
                }}
            }};

            Plotly.newPlot('{self.chart_id}', traces, layout, {{responsive: true}});
        }}

        function getTableData_{self.chart_id}() {{
            const data = window.filteredData || window.rawData;

            const monthlyData = {{}};

            data.forEach(row => {{
                const year = row['Год'];
                const month = row['Месяц'];
                const store = row['Магазин'];
                const revenue = row['Выручка'];

                const dateKey = `${{year}}-${{String(month).padStart(2, '0')}}`;

                if (!monthlyData[dateKey]) {{
                    monthlyData[dateKey] = {{}};
                }}

                if (!monthlyData[dateKey][store]) {{
                    monthlyData[dateKey][store] = 0;
                }}

                monthlyData[dateKey][store] += revenue;
            }});

            const dates = Object.keys(monthlyData).sort();
            const stores = [...new Set(data.map(r => r['Магазин']))].sort((a, b) => {{
                const numA = parseInt(a.match(/\\d+/));
                const numB = parseInt(b.match(/\\d+/));
                return numA - numB;
            }});

            const tableData = dates.map(date => {{
                const row = {{'Период': date}};
                stores.forEach(store => {{
                    row[store] = monthlyData[date][store] || 0;
                }});
                return row;
            }});

            return tableData;
        }}

        {table_js}
        """
