
        // Function to extract data from the SMA table
        document.addEventListener("DOMContentLoaded", function() {
            // Function to extract data from the SMA table
            function extractDataFromRSI9Table() {
                const table = document.querySelector('div.table-container .rsi_9_ScrollableTable table');
                const rows = table.querySelectorAll('tr');
                const data = {
                    candlestick: [],
                    volume: [],
                    rsi_9: []

                };
        
                for (let i = 1; i < rows.length; i++) {
                    const cells = rows[i].querySelectorAll('td');
                    const date = Date.parse(cells[0].textContent.trim());
                    const open = parseFloat(cells[2].textContent.trim());
                    const high = parseFloat(cells[3].textContent.trim());
                    const low = parseFloat(cells[4].textContent.trim());
                    const close = parseFloat(cells[1].textContent.trim());
                    const volume = parseFloat(cells[5].textContent.trim().replace(/,/g, ''));
                    const rsi_9 = parseFloat(cells[6].textContent.trim());

        
                    data.candlestick.push([date, open, high, low, close]);
                    data.volume.push([date, volume]);
                    data.rsi_9.push([date, rsi_9]);

                }
        
                return data;
            }
        
            const rsi_9_Data = extractDataFromRSI9Table();
        
            Highcharts.stockChart('candlestick-chart_rsi_9', {
                chart: {
                    backgroundColor: '#f5f5f5',  // Lighter background
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
                    gridLineColor: '#e6e6e6',  // Lighter gridlines
                    plotLines: [{
                        value: Math.max(...rsi_9_Data.candlestick.map(point => point[2])),  // 52-week high
                        color: '#FF4136',  // Light red for 52-week high
                        dashStyle: 'ShortDash',
                        width: 1,
                        label: {
                            text: '52-week high',
                            align: 'left'
                        }
                    }, {
                        value: Math.min(...rsi_9_Data.candlestick.map(point => point[3])),  // 52-week low
                        color: '#3D9970',  // Light green for 52-week low
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
                    color: '#FF4136',  // More beautiful shade of red
                    upColor: '#3D9970',  // More beautiful shade of green
                    lineColor: '#FF4136',  // Line color for downward movement
                    upLineColor: '#3D9970',  // Line color for upward movement
                    yAxis: 0
                },{
                    type: 'line',
                    data: rsi_9_Data.rsi_9,
                    name: 'RSI_9',
                    color: '#2c3e50',  // Neutral color for RSI
                    yAxis: 1
                }, {
                    type: 'column',
                    data: rsi_9_Data.volume,
                    name: 'Volume',
                    color: '#95a5a6',  // Neutral color for volume
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
                    maskFill: 'rgba(170, 205, 170, 0.3)',  // Light green mask
                    series: {
                        color: '#2ecc71',
                        lineColor: '#2ecc71'
                    },
                    height: 15  // Adjust this value to set the desired height
                },
                scrollbar: {
                    enabled: false
                }
            });
        });