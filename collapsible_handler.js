document.addEventListener("DOMContentLoaded", function () {
  var coll = document.getElementsByClassName("collapsible");
  var maxHeight = "10000px"; // An arbitrary value; adjust as needed based on your content

  for (var i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", toggleCollapsible);
    coll[i].addEventListener("touchend", handleTouchEnd);

    if (coll[i].classList.contains("active")) {
      toggleCollapsible.call(coll[i]);
    }
  }

  function handleTouchEnd(event) {
    event.preventDefault();
    toggleCollapsible.call(this, event);
  }

  function toggleCollapsible(event) {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight && content.style.maxHeight !== "0px") {
      content.style.maxHeight = "0px";
    } else {
      content.style.maxHeight = maxHeight;
    }
  }

  function processTable(table) {
    var rows = table.querySelectorAll("tbody tr"); // Get all rows in the table body
    rows.forEach(function (row) {
      var changeCell = row.querySelector("td:nth-child(6)"); // Change column
      var changePercentCell = row.querySelector("td:nth-child(7)"); // Change% column

      // For Change column
      if (parseFloat(changeCell.textContent) < 0) {
        changeCell.classList.add("negative");
      } else {
        changeCell.classList.add("positive");
      }

      // For Change% column
      var changePercentValue = parseFloat(
        changePercentCell.textContent.replace("%", "")
      ); // Extract the float value
      if (changePercentValue < 0) {
        changePercentCell.classList.add("negative");
      } else {
        changePercentCell.classList.add("positive");
      }
      changePercentCell.textContent = changePercentValue.toFixed(2) + "%"; // Append the % sign back
    });
  }

  // Target the main table
  var mainTable = document.querySelector(
    'div.scrollable-table[data-name="mainScrollableTable"] table'
  );
  if (mainTable) {
    processTable(mainTable);
  }
});
