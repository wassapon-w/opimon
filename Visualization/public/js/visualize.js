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
      getJSON('http://sd-lemon.naist.jp:3000/flowmods', function(err, output){
          data["flowmods"] = output;
          showFlowTable($(document.getElementById("flowTable")), data);
      });
    });
});

getJSON('http://sd-lemon.naist.jp:3000/topology', function(err, output){
    data["switch"] = output["node"];
    data["connect"] = output["link"];
    data["switchCounter"] = output["nodeCounter"];
    getSettings();
});

getJSON('http://sd-lemon.naist.jp:3000/flowmods', function(err, output){
    data["flowmods"] = output;
    showFlowTable($(document.getElementById("flowTable")), data);
});

function getSettings() {
    getJSON('http://sd-lemon.naist.jp:3000/settings.json', function(err, output){
        data["settings"] = output;
        console.log(data);
        visualize();
    });
}

function getNewSwitchData(data, switch_id) {
  getJSON('http://sd-lemon.naist.jp:3000/flowmods', function(err, output){
      data["flowmods"] = output;
      showFlowTableByID($(document.getElementById("flowTable")), data, switch_id);
  });

  getJSON('http://sd-lemon.naist.jp:3000/switch', function(err, output){
      data["switch"] = output;
      showSwitchPort($(document.getElementById("portTable")), data, switch_id);
  });
}

function visualize() {
    var svg = d3.select("svg"),
        width = svg.attr("width"),
        height = svg.attr("height");

    svg.append("svg:defs").selectAll("marker")
       .data(["arrow"])
       .enter().append("svg:marker")
       .attr("id", String)
       .attr("viewBox", "0 -5 10 10")
       .attr("refX", 22)
       .attr("refY", 0)
       .attr("markerWidth", 5)
       .attr("markerHeight", 5)
       .attr("orient", "auto")
       .append("svg:path")
       .attr("d", "M0,-5L10,0L0,5");

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var simulation = d3.forceSimulation()
                       .force("link", d3.forceLink().id(function(d) { return d.id; }))
                       .force("charge", d3.forceManyBody())
                       .force("center", d3.forceCenter(width / 2, height / 2));

    var path = svg.append("g").selectAll("path")
                  .data(data.connect)
                  .enter().append("path")
                  .attr("class", "link")
                  .attr("marker-end", "url(#arrow)");

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

      path
          .attr("d", function(d) {
              if(data["settings"][d.source.id] != undefined) {
                  var dx_source = data["settings"][d.source.id]["x"];
                  var dy_source = data["settings"][d.source.id]["y"];
              }
              else {
                  var dx_source = d.source.x;
                  var dy_source = d.source.y;
              }

              if(data["settings"][d.target.id] != undefined) {
                  var dx_target = data["settings"][d.target.id]["x"];
                  var dy_target = data["settings"][d.target.id]["y"];
              }
              else {
                  var dx_target = d.target.x;
                  var dy_target = d.target.y;
              }

              return "M" + dx_source + "," + dy_source + "A" + 0 + "," + 0 + " 0 0,1 " + dx_target + "," + dy_target;
      });

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
        // force.stop()
    }

    function dragged(d) {
        d.px += d3.event.dx;
        d.py += d3.event.dy;
        d.x += d3.event.dx;
        d.y += d3.event.dy;
        ticked();
    }

    function dragended(d) {
        d.fixed = true;
        ticked();
        // force.resume();
    }

    function mouseClick(d) {
        getNewSwitchData(data, d.id);
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

    // var showSwitch = document.getElementById("switch");
    // if(data["settings"][switch_id] != undefined) {
    //     showSwitch.textContent = "Switch ID : " + switch_id + " (" + data["settings"][switch_id]["name"] + ")";
    // }
    // else {
    //     showSwitch.textContent = "Switch ID : " + switch_id;
    // }

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

function showSwitchPort(container, data, switch_id) {
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
    row.append($("<th/>").text("Port"));
    row.append($("<th/>").text("Mac Address"));
    head.append(row);
    table.append(head);

    var body = $("<tbody/>");
    $.each(data["switch"][switch_id]["ports"], function(rowIndex, r) {
        var row = $("<tr/>");
        row.append($("<td/>").text(r["port_no"]));
        row.append($("<td/>").text(r["hw_addr"]));
        body.append(row);
    });
    table.append(body);

    return container.html(table);
}
