var data = {};

var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("get", url, true);
    xhr.responseType = "json";
    xhr.onload = function() {
      var status = xhr.status;
      if (status == 200) {
        callback(null, xhr.response);
      } else {
        callback(status);
      }
    };
    xhr.send();
};

getJSON('http://192.168.22.132:3000/flowmods', function(err, output){
    data["flowmods"] = output;
    // console.log(data["flowmods"]);
    showFlowTable();
});

getJSON('http://192.168.22.132:3000/topology', function(err, output){
    data["switch"] = output["node"];
    data["connect"] = output["link"];
    visualize();
});

function visualize() {
  console.log(data);

  var color = d3.scaleOrdinal(d3.schemeCategory20);

  var canvas = document.querySelector("canvas"),
      context = canvas.getContext("2d"),
      width = canvas.width,
      height = canvas.height;

  var simulation = d3.forceSimulation()
      .force("link", d3.forceLink().id(function(d) { return d.id; }))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter());

  simulation
      .nodes(data.switch)
      .on("tick", ticked);

  simulation.force("link")
      .links(data.connect);

  function ticked() {
    context.clearRect(0, 0, width, height);
    context.save();
    context.translate(width / 3, height / 3);

    context.beginPath();
    data.connect.forEach(drawLink);
    context.strokeStyle = "#aaa";
    context.stroke();

    context.beginPath();
    data.switch.forEach(drawNode);
    context.fillStyle = color(data.switch.forEach(function(d) { return d.id; }));
    context.fill();
    // context.strokeStyle = "#fff";
    // context.stroke();

    context.restore();
  }

  function drawLink(d) {
    context.moveTo(d.source.x, d.source.y);
    context.lineTo(d.target.x, d.target.y);
  }

  function drawNode(d) {
    context.moveTo(d.x + 100, d.y);
    context.arc(d.x, d.y, 10, 0, 2 * Math.PI);
  }
}

function showFlowTable() {
    var headerRow = ["Switch ID", "Destination MAC Address","Input Port", "Output Port"];

    var table = document.createElement("TABLE");
    table.border = "1";

    var row = table.insertRow(-1);
    for (var i = 0; i < headerRow.length; i++) {
      var headerCell = document.createElement("TH");
      headerCell.innerHTML = headerRow[i];
      row.appendChild(headerCell);
    }

    for (var i = 0; i < data["flowmods"]["1"].length; i++) {
        row = table.insertRow(-1);
        // for (var j = 0; j < 4; j++) {
            var cell0 = row.insertCell(-1);
            var cell1 = row.insertCell(-1);
            var cell2 = row.insertCell(-1);
            var cell3 = row.insertCell(-1);

            cell0.innerHTML = data["flowmods"]["1"][i]["switch_id"];
            cell1.innerHTML = data["flowmods"]["1"][i]["dst_mac"];
            cell2.innerHTML = data["flowmods"]["1"][i]["in_port"];
            cell3.innerHTML = data["flowmods"]["1"][i]["out_port"];
        // }
    }

    var dvTable = document.getElementById("flowTable");
    dvTable.innerHTML = "";
    dvTable.appendChild(table);
}
