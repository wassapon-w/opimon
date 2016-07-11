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
    showFlowTable($(document.getElementById("flowTable")), data);
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

    function mouseClick(d) {
        getNewFlowTableData($(document.getElementById("flowTable")), data, d.id);
    }
}

function showFlowTable(container, data) {
    var showTime = document.getElementById("currentTime");
    var currentTime = new Date(Date.now());
    showTime.textContent = "Time : " + currentTime.toString();

    var table = $("<table/>").addClass('table');

    var head = $("<thead/>");
    var row = $("<tr/>");
    row.append($("<th/>").text("Switch ID"));
    row.append($("<th/>").text("Match"));
    row.append($("<th/>").text("Actions"));
    row.append($("<th/>").text("Expire"));
    head.append(row);
    table.append(head);

    var body = $("<tbody/>");
    for(var i = 0; i < data["flowmods"]["switchFlowTable"].length; i++) {
      var switch_id = data["flowmods"]["switchFlowTable"][i]
      $.each(data["flowmods"][switch_id], function(rowIndex, r) {
          var expireMillisec = Date.parse(r["timestamp"]) + (r["hard_timeout"] * 1000);
          var expireTime = new Date(expireMillisec);

          if(expireTime > Date.now()) {
              var row = $("<tr/>");
              row.append($("<td/>").text(r["switch_id"]));
              row.append($("<td/>").text(JSON.stringify(r["match"])));
              row.append($("<td/>").text(JSON.stringify(r["actions"])));
              row.append($("<td/>").text(expireTime.toString()));
              body.append(row);
          }
      });
    }
    table.append(body);

    return container.html(table);
}

function showFlowTableByID(container, data, switch_id) {
    var showTime = document.getElementById("currentTime");
    var currentTime = new Date(Date.now());
    showTime.textContent = "Time : " + currentTime.toString();

    var table = $("<table/>").addClass('table');

    var head = $("<thead/>");
    var row = $("<tr/>");
    row.append($("<th/>").text("Switch ID"));
    row.append($("<th/>").text("Match"));
    row.append($("<th/>").text("Actions"));
    row.append($("<th/>").text("Expire"));
    head.append(row);
    table.append(head);

    var body = $("<tbody/>");
    $.each(data["flowmods"][switch_id], function(rowIndex, r) {
        var expireMillisec = Date.parse(r["timestamp"]) + (r["hard_timeout"] * 1000);
        var expireTime = new Date(expireMillisec);

        if(expireTime > Date.now()) {
            var row = $("<tr/>");
            row.append($("<td/>").text(r["switch_id"]));
            row.append($("<td/>").text(JSON.stringify(r["match"])));
            row.append($("<td/>").text(JSON.stringify(r["actions"])));
            row.append($("<td/>").text(expireTime.toString()));
            body.append(row);
        }
    });
    table.append(body);

    return container.html(table);
}

function getNewFlowTableData(container, data, switch_id) {
  getJSON('http://192.168.22.132:3000/flowmods', function(err, output){
      data["flowmods"] = output;
      showFlowTableByID(container, data, switch_id);
  });
}
