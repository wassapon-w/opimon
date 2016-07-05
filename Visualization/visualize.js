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
    console.log(data);

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var svg = d3.select("svg"),
        width = svg.attr("width"),
        height = svg.attr("height");

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
                  .attr("r", 10)
                  .style("fill", function(d) { return color(d.id); })
                  .call(d3.drag()
                          .on("start", dragstarted)
                          .on("drag", dragged)
                          .on("end", dragended));

    node.append("title")
        .text(function(d) { return d.id; });

    // node.append("text")
    //     .attr("dy", ".3em")
    //     .style("text-anchor", "middle")
    //     .text(function(d) { return d.id.substring(10, d.r / 3); });

    var gnodes = svg.selectAll('g.gnode')
     .data(data.switch)
     .enter()
     .append('g')
     .classed('gnode', true);

     var labels = gnodes.append("text")
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

      gnodes
          .attr("transform", function(d) { return 'translate(' + [d.x, d.y] + ')'; });
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
}

function showFlowTable() {
    var headerRow = ["Switch ID", "Match", "Action"];

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
        if(data["flowmods"][i + ""] != undefined) {
            for (var j = 0; j < data["flowmods"][i + ""].length; j++) {
                row = table.insertRow(-1);
                // for(var k = 0; k < 3; k++) {
                  var cell0 = row.insertCell(-1);
                  var cell1 = row.insertCell(-1);
                  var cell2 = row.insertCell(-1);

                  cell0.innerHTML = data["flowmods"][i + ""][j]["switch_id"];
                  cell1.innerHTML = JSON.stringify(data["flowmods"][i + ""][j]["match"]);
                  cell2.innerHTML = JSON.stringify(data["flowmods"][i + ""][j]["actions"]);
                // }
            }
        }
    }

    var dvTable = document.getElementById("flowTable");
    dvTable.innerHTML = "";
    dvTable.appendChild(table);
}
