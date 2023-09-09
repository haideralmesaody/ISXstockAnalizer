
        // Function to extract data from the SMA table
        document.addEventListener("DOMContentLoaded", function() {
        // Function to extract data from the SMA table
        function extractDataFromSMATable() {
            const table = document.querySelector('div.table-container .smaScrollableTable table');
            const rows = table.querySelectorAll('tr');
            const data = {
                candlestick: [],
                volume: [],
                sma10: [],
                sma50: [],
                sma200: []
            };
    
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].querySelectorAll('td');
                const date = Date.parse(cells[0].textContent.trim());
                const open = parseFloat(cells[2].textContent.trim());
                const high = parseFloat(cells[3].textContent.trim());
                const low = parseFloat(cells[4].textContent.trim());
                const close = parseFloat(cells[1].textContent.trim());
                const volume = parseFloat(cells[5].textContent.trim().replace(/,/g, ''));
                const sma10Value = parseFloat(cells[6].textContent.trim());
                const sma50Value = parseFloat(cells[7].textContent.trim());
                const sma200Value = parseFloat(cells[8].textContent.trim());
    
                data.candlestick.push([date, open, high, low, close]);
                data.volume.push([date, volume]);
                data.sma10.push([date, sma10Value]);
                data.sma50.push([date, sma50Value]);
                data.sma200.push([date, sma200Value]);
            }
    
            return data;
        }
    
        const smaData = extractDataFromSMATable();
    
        Highcharts.stockChart('candlestick-chart_sma', {
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
                height: '90%',
                lineWidth: 2,
                gridLineColor: '#e6e6e6'  // Lighter gridlines
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
                data: smaData.candlestick,
                name: 'Stock Price',
                color: '#FF4136',  // More beautiful shade of red
                upColor: '#3D9970',  // More beautiful shade of green
                lineColor: '#FF4136',  // Line color for downward movement
                upLineColor: '#3D9970',  // Line color for upward movement
                yAxis: 0
            }, {
                type: 'line',
                data: smaData.sma10,
                name: 'SMA10',
                yAxis: 0,
                color: '#3498db'  // Shade of blue for SMA10
            }, {
                type: 'line',
                data: smaData.sma50,
                name: 'SMA50',
                yAxis: 0,
                color: '#e67e22'  // Shade of orange for SMA50
            }, {
                type: 'line',
                data: smaData.sma200,
                name: 'SMA200',
                yAxis: 0,
                color: '#8e44ad'  // Shade of purple for SMA200
            }, {
                type: 'column',
                data: smaData.volume,
                name: 'Volume',
                color: '#95a5a6',  // Neutral color for volume
                yAxis: 1
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