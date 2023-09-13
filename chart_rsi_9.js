/**
 * Function to extract data related to RSI_9 from a specific table.
 * This function targets a table with the class 'rsi_9_ScrollableTable' inside a 'div' with 
 * the class 'table-container'.
 *
 * @returns {Object} A structured object containing:
 * - candlestick: Array of stock data [date, open, high, low, close].
 * - volume: Array of trading volumes [date, volume].
 * - rsi_9: Array of RSI_9 values [date, rsi_9 value].
 */
function extractDataFromRSI9Table() {
    // Select the desired table using querySelector.
    const table = document.querySelector('div.table-container .rsi_9_ScrollableTable table');
    const rows = table.querySelectorAll('tr');
    const data = {
        candlestick: [],
        volume: [],
        rsi_9: []
    };
    // Loop through table rows starting from the second row (ignoring headers).
    for (let i = 1; i < rows.length; i++) {
        // Extract and process the required data from each row.
        const cells = rows[i].querySelectorAll('td');
        const date = Date.parse(cells[0].textContent.trim());
        const open = parseFloat(cells[2].textContent.trim());
        const high = parseFloat(cells[3].textContent.trim());
        const low = parseFloat(cells[4].textContent.trim());
        const close = parseFloat(cells[1].textContent.trim());
        const volume = parseFloat(cells[5].textContent.trim().replace(/,/g, ''));
        const rsi_9 = parseFloat(cells[6].textContent.trim());
        // Append data to the respective arrays.
        data.candlestick.push([date, open, high, low, close]);
        data.volume.push([date, volume]);
        data.rsi_9.push([date, rsi_9]);
    }

    return data;
}
// Set an event listener to the button with the ID 'rsi9Button'.
// When the button is clicked, the chart will be rendered.
document.getElementById('rsi9Button').addEventListener('click', function() {
    // Extract data from the RSI_9 table.
    const rsi_9_Data = extractDataFromRSI9Table();
    // Configure and display a stock chart using the Highcharts library.
    Highcharts.stockChart('candlestick-chart_rsi_9', {
        // Basic chart configurations, such as background color, font, etc.
        chart: {
            backgroundColor: '#f5f5f5',
            style: {
                fontFamily: 'Arial, sans-serif'
            },
            panning: true,
            pinchType: 'x'
        },
        legend: {
            enabled: true,
            layout: 'horizontal',
            align: 'center',
            verticalAlign: 'top',
            borderWidth: 0,
            floating: true
        },
        zoomType: 'xy',
        // Configuration for the chart tooltip.
        tooltip: {
            split: true,
            valueDecimals: 2,
            borderColor: '#8a8a8a',
            shadow: false,
            headerFormat: '<b>{point.x:%A, %b %e, %Y}</b><br/>',
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            borderRadius: 5,
            style: {
                fontWeight: 'bold'
            },
            crosshairs: [{
                width: 2,
                color: 'gray',
                dashStyle: 'shortdot'
            }, {
                width: 2,
                color: 'gray',
                dashStyle: 'shortdot'
            }]
        },
        // Y-Axis configurations, including stock price, RSI_9, and volume data.
        yAxis: [{
            title: {
                text: 'Stock Price'
            },
            height: '60%',
            lineWidth: 2,
            gridLineColor: '#e6e6e6',
            plotLines: [{
                value: Math.max(...rsi_9_Data.candlestick.map(point => point[2])),
                color: '#FF4136',
                dashStyle: 'ShortDash',
                width: 1,
                label: {
                    text: '52-week high',
                    align: 'left'
                }
            }, {
                value: Math.min(...rsi_9_Data.candlestick.map(point => point[3])),
                color: '#3D9970',
                dashStyle: 'ShortDash',
                width: 1,
                label: {
                    text: '52-week low',
                    align: 'left'
                }
            }]
        }, {
            title: {
                text: 'RSI_9'
            },
            top: '60%',
            height: '30%',
            offset: 0,
            lineWidth: 2,
            plotLines: [{
                value: 70,
                color: 'red',
                width: 1,
                label: {
                    text: 'Overbought',
                    align: 'right',
                    style: {
                        color: 'red'
                    }
                }
            }, {
                value: 30,
                color: 'green',
                width: 1,
                label: {
                    text: 'Oversold',
                    align: 'right',
                    style: {
                        color: 'green'
                    }
                }
            }]
        }, {
            title: {
                text: 'Volume'
            },
            top: '90%',
            height: '10%',
            offset: 0,
            lineWidth: 2
        }],
        series: [{
            type: 'candlestick',
            data: rsi_9_Data.candlestick,
            name: 'Stock Price',
            color: '#FF4136',
            upColor: '#3D9970',
            lineColor: '#FF4136',
            upLineColor: '#3D9970',
            yAxis: 0
        },{
            type: 'line',
            data: rsi_9_Data.rsi_9,
            name: 'RSI_9',
            color: '#2c3e50',
            yAxis: 1
        }, {
            type: 'column',
            data: rsi_9_Data.volume,
            name: 'Volume',
            color: '#95a5a6',
            yAxis: 2
        }],
        rangeSelector: {
            buttonTheme: {
                fill: '#e6e6e6',
                stroke: '#c4c4c4',
                style: {
                    color: '#333',
                    fontWeight: 'bold'
                },
                states: {
                    hover: {
                        fill: '#d4d4d4'
                    },
                    select: {
                        fill: '#c4c4c4',
                        style: {
                            color: 'white'
                        }
                    }
                }
            },
            inputBoxBorderColor: '#c4c4c4',
            inputBoxHeight: 18,
            inputBoxWidth: 120,
            inputStyle: {
                fontSize: '10px',
                color: '#333'
            },
            labelStyle: {
                color: '#666',
                fontWeight: 'bold'
            }
        },
        navigator: {
            maskFill: 'rgba(170, 205, 170, 0.3)',
            series: {
                color: '#2ecc71',
                lineColor: '#2ecc71'
            },
            height: 15
        },
        scrollbar: {
            enabled: false
        }
    });
});
