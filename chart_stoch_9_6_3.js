function extractDataFromSTOCHTable() {
    const table = document.querySelector('div.table-container .stoch_9_6_3_ScrollableTable table');
    const rows = table.querySelectorAll('tr');
    const data = {
        candlestick: [],
        volume: [],
        stoch: []
    };

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].querySelectorAll('td');
        const date = Date.parse(cells[0].textContent.trim());
        const open = parseFloat(cells[2].textContent.trim());
        const high = parseFloat(cells[3].textContent.trim());
        const low = parseFloat(cells[4].textContent.trim());
        const close = parseFloat(cells[1].textContent.trim());
        const volume = parseFloat(cells[5].textContent.trim().replace(/,/g, ''));
        const STOCHk_9_6_3 = parseFloat(cells[6].textContent.trim());
        const STOCHd_9_6_3 = parseFloat(cells[7].textContent.trim());

        data.candlestick.push([date, open, high, low, close]);
        data.volume.push([date, volume]);
        data.stoch.push([date, STOCHk_9_6_3, STOCHd_9_6_3]);
    }

    return data;
}

document.getElementById('STOCH_9_6_3Button').addEventListener('click', function() {
    const stoch_Data = extractDataFromSTOCHTable();

    Highcharts.stockChart('candlestick-chart_stoch_9_6_3', {
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
        yAxis: [{
            title: {
                text: 'Stock Price'
            },
            height: '60%',
            lineWidth: 2,
            gridLineColor: '#e6e6e6',
            plotLines: [{
                value: Math.max(...stoch_Data.candlestick.map(point => point[2])),
                color: '#FF4136',
                dashStyle: 'ShortDash',
                width: 1,
                label: {
                    text: '52-week high',
                    align: 'left'
                }
            }, {
                value: Math.min(...stoch_Data.candlestick.map(point => point[3])),
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
                text: 'STOCH_9_6_3'
            },
            top: '60%',
            height: '30%',
            offset: 0,
            lineWidth: 2,
            plotLines: [{
                value: 80,
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
                value: 20,
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
            data: stoch_Data.candlestick,
            name: 'Stock Price',
            color: '#FF4136',
            upColor: '#3D9970',
            lineColor: '#FF4136',
            upLineColor: '#3D9970',
            yAxis: 0
        },{
            type: 'line',
            data: stoch_Data.stoch.map(point => [point[0], point[1]]),
            name: 'STOCHk_9_6_3',
            color: '#2c3e50',
            yAxis: 1
        },
        {
            type: 'line',
            data: stoch_Data.stoch.map(point => [point[0], point[2]]),
            name: 'STOCHd_9_6_3',
            color: '#FF4136',
            yAxis: 1
        }, {
            type: 'column',
            data: stoch_Data.volume,
            name: 'Volume',
            color: '#000000',
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
