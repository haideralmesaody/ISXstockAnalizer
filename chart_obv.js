document.addEventListener("DOMContentLoaded", function () {
  const obvButton = document.getElementById("obvButton");

  obvButton.addEventListener("click", function () {
    const content = this.nextElementSibling;

    if (content.style.display === "" || content.style.display === "none") {
      const obv_Data = extractDataFromOBVTable();

      Highcharts.stockChart("candlestick-chart_obv", {
        chart: {
          backgroundColor: "#f5f5f5",
          style: {
            fontFamily: "Arial, sans-serif",
          },
          panning: true,
          pinchType: "x",
        },
        legend: {
          enabled: true,
          layout: "horizontal",
          align: "center",
          verticalAlign: "top",
          borderWidth: 0,
          floating: true,
        },
        zoomType: "xy",
        tooltip: {
          split: true,
          valueDecimals: 2,
          borderColor: "#8a8a8a",
          shadow: false,
          headerFormat: "<b>{point.x:%A, %b %e, %Y}</b><br/>",
          backgroundColor: "rgba(255, 255, 255, 0.7)",
          borderRadius: 5,
          style: {
            fontWeight: "bold",
          },
        },
        yAxis: [
          {
              title: { text: "Stock Price" },
              height: "60%",
              lineWidth: 2,
              gridLineColor: "#e6e6e6",
          },
          {
              title: { text: "OBV" },
              top: "60%",
              height: "30%",
              offset: 4,
              lineWidth: 2,
          },
          {
              title: { text: "Volume" },
              top: "90%",
              height: "10%",
              offset: 8,
              lineWidth: 2,
          },
      ],
        series: [
          {
            type: "candlestick",
            data: obv_Data.candlestick,
            name: "Stock Price",
            color: "#FF4136",
            upColor: "#3D9970",
            lineColor: "#FF4136",
            upLineColor: "#3D9970",
            yAxis: 0,
          },
          {
            type: "line",
            data: obv_Data.obv,
            name: "OBV",
            color: "#2c3e50",
            yAxis: 1,
          },
          {
            type: "line",
            data: obv_Data.obv_sma,
            name: "OBV_SMA",
            color: "#FF9800",
            yAxis: 1,
          },
          {
            type: "column",
            data: obv_Data.volume,
            name: "Volume",
            color: "#95a5a6",
            yAxis: 2,
          },
        ],
        rangeSelector: {
          buttonTheme: {
            fill: "#e6e6e6",
            stroke: "#c4c4c4",
            style: {
              color: "#333",
              fontWeight: "bold",
            },
            states: {
              hover: {
                fill: "#d4d4d4",
              },
              select: {
                fill: "#c4c4c4",
                style: {
                  color: "white",
                },
              },
            },
          },
          inputBoxBorderColor: "#c4c4c4",
          inputBoxHeight: 18,
          inputBoxWidth: 120,
          inputStyle: {
            fontSize: "10px",
            color: "#333",
          },
          labelStyle: {
            color: "#666",
            fontWeight: "bold",
          },
        },
        navigator: {
          maskFill: "rgba(170, 205, 170, 0.3)",
          series: {
            color: "#2ecc71",
            lineColor: "#2ecc71",
          },
          height: 15,
        },
        scrollbar: {
          enabled: false,
        },
      });
    }
  });

  function extractDataFromOBVTable() {
    const table = document.querySelector(
      "div.table-container .obv_ScrollableTable table"
    );
    const rows = table.querySelectorAll("tr");
    const data = {
      candlestick: [],
      volume: [],
      obv: [],
      obv_sma: [],
    };

    for (let i = 1; i < rows.length; i++) {
      const cells = rows[i].querySelectorAll("td");
      const date = Date.parse(cells[0].textContent.trim());
      const open = parseFloat(cells[2].textContent.trim());
      const high = parseFloat(cells[3].textContent.trim());
      const low = parseFloat(cells[4].textContent.trim());
      const close = parseFloat(cells[1].textContent.trim());
      const volume = parseFloat(cells[5].textContent.trim().replace(/,/g, ""));
      const obv = parseFloat(cells[6].textContent.trim());
      const obv_sma = parseFloat(cells[7].textContent.trim());

      data.candlestick.push([date, open, high, low, close]);
      data.volume.push([date, volume]);
      data.obv.push([date, obv]);
      data.obv_sma.push([date, obv_sma]);
    }

    return data;
  }
});
