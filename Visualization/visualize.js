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

getJSON('http://192.168.22.132:3000/topology', function(err, output){
    data["switch"] = output["node"];
    data["connect"] = output["link"];
    data["switchCounter"] = output["nodeCounter"];
    visualize();
});

getJSON('http://192.168.22.132:3000/flowmods', function(err, output){
    data["flowmods"] = output;
    showFlowTable();
});

function visualize() {
    var svg = d3.select("svg"),
        width = svg.attr("width"),
        height = svg.attr("height");

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var simulation = d3.forceSimulation()
                       .force("link", d3.forceLink().id(function(d) { return d.id; }))
                       .force("charge", d3.forceManyBody())
                       .force("center", d3.forceCenter(width / 2, height / 2));

    var link = svg.append("g")
                  .attr("class", "links")
                  .selectAll("line")
                  .data(data.connect)
                  .enter().append("line");

    var node = svg.append("g")
                  .attr("class", "nodes")
                  .selectAll("circle")
                  .data(data.switch)
                  .enter().append("circle")
                  .on("click", mouseClick)
                  .attr("r", 10)
                  .style("fill", function(d) { return color(d.id); })
                  .call(d3.drag()
                          .on("start", dragstarted)
                          .on("drag", dragged)
                          .on("end", dragended));

    node.append("title")
        .text(function(d) { return d.id; });

    var switchLabel = svg.selectAll('g.gnode')
                         .data(data.switch)
                         .enter()
                         .append('g')
                         .classed('gnode', true);

     var labels = switchLabel.append("text")
                             .on("click", mouseClick)
                             .text(function(d) { return d.id; });

    simulation
        .nodes(data.switch)
        .on("tick", ticked);

    simulation.force("link")
              .links(data.connect);

    function ticked() {
      link
          .attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node
          .attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });

      switchLabel
          .attr("transform", function(d) { return 'translate(' + [d.x-4, d.y+5] + ')'; });
    }

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    function mouseClick() {
        console.log("click");
    }
}

function showFlowTable() {
    var headerRow = ["Switch ID", "Match", "Action", "Expire"];

    var table = document.createElement("TABLE");
    table.border = "1";

    var row = table.insertRow(-1);
    for (var i = 0; i < headerRow.length; i++) {
        var headerCell = document.createElement("TH");
        headerCell.innerHTML = headerRow[i];
        row.appendChild(headerCell);
    }

    for (var i = 0; i < data["flowmods"]["switchFlowTable"].length; i++) {
        var switch_id = data["flowmods"]["switchFlowTable"][i]
        if(data["flowmods"][switch_id] != undefined) {
            for (var j = 0; j < data["flowmods"][switch_id].length; j++) {
                if(data["flowmods"][switch_id][j]["actions"].length != 0) {
                    row = table.insertRow(-1);
                    var cell0 = row.insertCell(-1);
                    var cell1 = row.insertCell(-1);
                    var cell2 = row.insertCell(-1);
                    var cell3 = row.insertCell(-1);
                    var cell4 = row.insertCell(-1);

                    var expireMillisec = Date.parse(data["flowmods"][switch_id][j]["timestamp"]) + (data["flowmods"][switch_id][j]["hard_timeout"] * 1000);
                    var expireTime = new Date(expireMillisec);

                    cell0.innerHTML = data["flowmods"][switch_id][j]["switch_id"];
                    cell1.innerHTML = JSON.stringify(data["flowmods"][switch_id][j]["match"]);
                    cell2.innerHTML = JSON.stringify(data["flowmods"][switch_id][j]["actions"]);
                    cell3.innerHTML = expireTime.toString();
                    cell4.innerHTML = new Date(Date.parse(data["flowmods"][switch_id][j]["timestamp"]));
                }
            }
        }
    }

    var dvTable = document.getElementById("flowTable");
    dvTable.innerHTML = "";
    dvTable.appendChild(table);
}
