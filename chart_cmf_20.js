// Wait for the entire document to load before executing the JavaScript.
document.addEventListener("DOMContentLoaded", function() {
    // Get the button element by its ID.
    const cmf20Button = document.getElementById('cmf20Button');
    // Event listener for the button click.
    cmf20Button.addEventListener('click', function() {
        const content = this.nextElementSibling;
        // Check if the chart content is currently hidden or not displayed.
        if (content.style.display === "" || content.style.display === "none") {
            // Extract data from the table.
            const cmf_20_Data = extractDataFromCMF20Table();
            // Create and display the Highcharts stock chart with the extracted data.
            Highcharts.stockChart('candlestick-chart_cmf_20', {
                chart: {
                    backgroundColor: '#f5f5f5',
                    style: {
                        fontFamily: 'Arial, sans-serif'
                    },
                    panning: true,
                    pinchType: 'x',
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
                    plotBorderWidth: 1,
                    plotBorderColor: 'black',
                    plotLines: [{
                        value: Math.max(...cmf_20_Data.candlestick.map(point => point[2])),
                        color: '#FF4136',
                        dashStyle: 'ShortDash',
                        width: 1,
                        label: {
                            text: '52-week high',
                            align: 'left'
                        }
                    }, {
                        value: Math.min(...cmf_20_Data.candlestick.map(point => point[3])),
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
                        text: 'CMF_20'
                    },
                    top: '60%',
                    height: '30%',
                    offset: 0,
                    lineWidth: 2,
                    plotLines: [{
                        value: 0,
                        color: 'blue',
                        width: 1,
                        label: {
                            text: 'Zero Line',
                            align: 'right',
                            style: {
                                color: 'blue'
                            }
                        }
                    }, {
                        value: 0.05,
                        color: 'green',
                        width: 1,
                        label: {
                            text: 'Strong Buy Signal',
                            align: 'right',
                            style: {
                                color: 'green'
                            }
                        }
                    }, {
                        value: -0.05,
                        color: 'red',
                        width: 1,
                        label: {
                            text: 'Strong Sell Signal',
                            align: 'right',
                            style: {
                                color: 'red'
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
                    data: cmf_20_Data.candlestick,
                    name: 'Stock Price',
                    color: '#FF4136',
                    upColor: '#3D9970',
                    lineColor: '#FF4136',
                    upLineColor: '#3D9970',
                    yAxis: 0
                }, {
                    type: 'line',
                    data: cmf_20_Data.cmf_20,
                    name: 'CMF_20',
                    color: '#2c3e50',
                    yAxis: 1
                }, {
                    type: 'column',
                    data: cmf_20_Data.volume,
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
        }
    });
    /**
     * Extracts data from a table with the class 'cmf_20_ScrollableTable'.
     * 
     * @returns {Object} An object containing arrays for candlestick data, volume, and CMF_20.
     */
    function extractDataFromCMF20Table() {
        const table = document.querySelector('div.table-container .cmf_20_ScrollableTable table');
        const rows = table.querySelectorAll('tr');
        const data = {
            candlestick: [],
            volume: [],
            cmf_20: []
        };
        // Loop through each row (skip the header row) and extract the data.
        for (let i = 1; i < rows.length; i++) {
            const cells = rows[i].querySelectorAll('td');
            // Parse and extract the required data from each cell.
            const date = Date.parse(cells[0].textContent.trim());
            const open = parseFloat(cells[2].textContent.trim());
            const high = parseFloat(cells[3].textContent.trim());
            const low = parseFloat(cells[4].textContent.trim());
            const close = parseFloat(cells[1].textContent.trim());
            const volume = parseFloat(cells[5].textContent.trim().replace(/,/g, ''));
            const cmf_20 = parseFloat(cells[6].textContent.trim());
            // Push the parsed data into the respective arrays.
            data.candlestick.push([date, open, high, low, close]);
            data.volume.push([date, volume]);
            data.cmf_20.push([date, cmf_20]);
        }

        return data;
    }
});
