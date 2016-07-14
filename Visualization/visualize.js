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

$(document).ready(function(){
    $('#showfull').click(function(){
      getJSON('http://192.168.22.132:3000/flowmods', function(err, output){
          data["flowmods"] = output;
          showFlowTable($(document.getElementById("flowTable")), data);
      });
    });
});

getJSON('http://192.168.22.132:3000/topology', function(err, output){
    data["switch"] = output["node"];
    data["connect"] = output["link"];
    data["switchCounter"] = output["nodeCounter"];
    getSettings();
});

getJSON('http://192.168.22.132:3000/flowmods', function(err, output){
    data["flowmods"] = output;
    showFlowTable($(document.getElementById("flowTable")), data);
});

function getSettings() {
    getJSON('http://192.168.22.132:3000/settings.json', function(err, output){
        data["settings"] = output;
        visualize();
    });
}

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
                             .text(function(d) {
                               if(data["settings"][d.id] != undefined) { return data["settings"][d.id]["name"]; }
                               else { return d.id; } });

    simulation
        .nodes(data.switch)
        .on("tick", ticked);

    simulation
        .force("link")
        .links(data.connect);

    function ticked() {

      link
          .attr("x1", function(d) {
              if(data["settings"][d.source.id] != undefined) { return data["settings"][d.source.id]["x"]; }
              else { return d.source.x; } })
          .attr("y1", function(d) {
              if(data["settings"][d.source.id] != undefined) { return data["settings"][d.source.id]["y"]; }
              else { return d.source.y; } })
          .attr("x2", function(d) {
              if(data["settings"][d.target.id] != undefined) { return data["settings"][d.target.id]["x"]; }
              else { return d.target.x; } })
          .attr("y2", function(d) {
              if(data["settings"][d.target.id] != undefined) { return data["settings"][d.target.id]["y"]; }
              else { return d.target.y; } });

      node
          .attr("cx", function(d) {
              if(data["settings"][d.id] != undefined) { return data["settings"][d.id]["x"]; }
              else { return d.x; } })
          .attr("cy", function(d) {
              if(data["settings"][d.id] != undefined) { return data["settings"][d.id]["y"]; }
              else { return d.y; } });

      switchLabel
          .attr("transform", function(d) {
              if(data["settings"][d.id] != undefined) { return 'translate(' + [data["settings"][d.id]["x"], data["settings"][d.id]["y"]] + ')'; }
              else { return 'translate(' + [d.x, d.y] + ')'; } });
    }

    function dragstarted(d) {
        // if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        // d.fx = d.x;
        // d.fy = d.y;
        force.stop()
    }

    function dragged(d) {
        // d.fx = d3.event.x;
        // d.fy = d3.event.y;
        d.px += d3.event.dx;
        d.py += d3.event.dy;
        d.x += d3.event.dx;
        d.y += d3.event.dy;
        ticked();
    }

    function dragended(d) {
        // if (!d3.event.active) simulation.alphaTarget(0);
        // d.fx = null;
        // d.fy = null;
        d.fixed = true;
        ticked();
        force.resume();
    }

    function mouseClick(d) {
        getNewFlowTableData($(document.getElementById("flowTable")), data, d.id);
    }
}

function showFlowTable(container, data) {
    var showTime = document.getElementById("currentTime");
    var currentTime = new Date(Date.now());
    showTime.textContent = "Time : " + currentTime.toString();

    var showSwitch = document.getElementById("switch");
    showSwitch.textContent = "";

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

              var match = $("<td/>");
              match.append($("<li/>").text("Wildcard : " + r["match"]["wildcards"] + "\n"));
              match.append($("<li/>").text("Switch Input Port : " + r["match"]["in_port"] + "\n"));
              match.append($("<li/>").text("Source MAC Address : " + r["match"]["dl_src"] + "\n"));
              match.append($("<li/>").text("Destination MAC Address : " + r["match"]["dl_dst"] + "\n"));
              match.append($("<li/>").text("VLAN ID : " + r["match"]["dl_vlan"] + "\n"));
              match.append($("<li/>").text("VLAN Priority : " + r["match"]["dl_vlan_pcp"] + "\n"));
              match.append($("<li/>").text("Ethernet Frame Type : " + r["match"]["dl_type"] + "\n"));
              match.append($("<li/>").text("IP ToS : " + r["match"]["nw_tos"] + "\n"));
              match.append($("<li/>").text("IP Protocol : " + r["match"]["nw_proto"] + "\n"));
              match.append($("<li/>").text("Source IP Address : " + r["match"]["nw_src"] + "\n"));
              match.append($("<li/>").text("Destination IP Address : " + r["match"]["nw_dst"] + "\n"));
              match.append($("<li/>").text("Source TCP/UDP Port : " + r["match"]["tp_src"] + "\n"));
              match.append($("<li/>").text("Destination TCP/UDP Port : " + r["match"]["tp_dst"] + "\n"));
              row.append(match);

              var action = $("<td/>");
              action.append($("<li/>").text("Type : " + r["actions"][0]["type"] + "\n"));
              action.append($("<li/>").text("Switch Output Port : " + r["actions"][0]["port"] + "\n"));
              action.append($("<li/>").text("Max Length : " + r["actions"][0]["max_len"] + "\n"));
              row.append(action);

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

    var showSwitch = document.getElementById("switch");
    if(data["settings"][switch_id] != undefined) {
        showSwitch.textContent = "Switch ID : " + switch_id + " (" + data["settings"][switch_id]["name"] + ")";
    }
    else {
        showSwitch.textContent = "Switch ID : " + switch_id;
    }

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

            var match = $("<td/>");
            match.append($("<li/>").text("Wildcard : " + r["match"]["wildcards"] + "\n"));
            match.append($("<li/>").text("Switch Input Port : " + r["match"]["in_port"] + "\n"));
            match.append($("<li/>").text("Source MAC Address : " + r["match"]["dl_src"] + "\n"));
            match.append($("<li/>").text("Destination MAC Address : " + r["match"]["dl_dst"] + "\n"));
            match.append($("<li/>").text("VLAN ID : " + r["match"]["dl_vlan"] + "\n"));
            match.append($("<li/>").text("VLAN Priority : " + r["match"]["dl_vlan_pcp"] + "\n"));
            match.append($("<li/>").text("Ethernet Frame Type : " + r["match"]["dl_type"] + "\n"));
            match.append($("<li/>").text("IP ToS : " + r["match"]["nw_tos"] + "\n"));
            match.append($("<li/>").text("IP Protocol : " + r["match"]["nw_proto"] + "\n"));
            match.append($("<li/>").text("Source IP Address : " + r["match"]["nw_src"] + "\n"));
            match.append($("<li/>").text("Destination IP Address : " + r["match"]["nw_dst"] + "\n"));
            match.append($("<li/>").text("Source TCP/UDP Port : " + r["match"]["tp_src"] + "\n"));
            match.append($("<li/>").text("Destination TCP/UDP Port : " + r["match"]["tp_dst"] + "\n"));
            row.append(match);

            var action = $("<td/>");
            action.append($("<li/>").text("Type : " + r["actions"][0]["type"] + "\n"));
            action.append($("<li/>").text("Switch Output Port : " + r["actions"][0]["port"] + "\n"));
            action.append($("<li/>").text("Max Length : " + r["actions"][0]["max_len"] + "\n"));
            row.append(action);

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
