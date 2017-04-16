var dataURL = '';
var data = {};
var currentSelectSwitch = "";
var isSelected = false;
var resetLocation = false;
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
  getData();

  setInterval(function() {
    resetLocation = false;
    sendNodeLocation();
  }, 60 * 1000);

  $('#showfull').click(function(){
    getJSON(dataURL + '/flowmods', function(err, output){
        data["flowmods"] = output;
        // showFlowTable($(document.getElementById("flowTable")), data);
    });
  });
});

function getData() {
  // getJSON(dataURL + '/topology', function(err, output){
  //     data["switch"] = output["node"];
  //     data["connect"] = output["link"];
  //     data["switchCounter"] = output["nodeCounter"];
  //     getSettings();
  // });

  // getJSON(dataURL + '/flowmods', function(err, output){
  //     data["flowmods"] = output;
  //     // showFlowTable($(document.getElementById("flowTable")), data);
  // });

  getJSON(dataURL + '/gettime', function(err, output){
      data["minTime"] = Date.parse(output);
      // console.log(data["minTime"]);
      var minTime = new Date(data["minTime"]);
      var currentTime = new Date(Date.now());
      document.getElementById("showTime").textContent = currentTime;
      $('#timeSlider').attr('min', minTime.valueOf());
      $('#timeSlider').attr('max', currentTime.valueOf());
      $('#timeSlider').attr('value', currentTime.valueOf());
      sendDataToServer();
  });

  getSettings();
}

function getSettings() {
    getJSON(dataURL + '/settings.json', function(err, output){
        data["settings"] = output;
        console.log(data);
        // visualize();
    });
}

function getNewSwitchData(data, switch_id) {
    // getJSON(dataURL + '/flowmods', function(err, output){
    //     data["flowmods"] = output;
    //     showFlowTableByID($(document.getElementById("flowTable")), data, switch_id);
    // });
    showFlowTableByID($(document.getElementById("flowTable")), data, switch_id);

    // getJSON(dataURL + '/switch', function(err, output){
    //     // data["switch"] = output;
    //     // console.log(data["switch"]);
    //     showSwitchPort($(document.getElementById("portTable")), data, switch_id);
    // });
    showSwitchPort($(document.getElementById("portTable")), data, switch_id);
}

function visualize() {
    var loadLabel = document.getElementById("loading");
    loadLabel.textContent = "";

    var svg = d3.select("#topology"),
        width = $("#showNetworkTopology").width(),
        height = $("#showNetworkTopology").height();

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
       .append("svg:path").style("fill", function(d) { return d3.rgb(119, 136, 153); })
       .attr("d", "M0,-5L10,0L0,5");

    var color = d3.scaleOrdinal(d3.schemeCategory20);

    var simulation = d3.forceSimulation()
                       .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(45))
                       .force("charge", d3.forceManyBody())
                       .force("center", d3.forceCenter(width / 2, height / 2));

    var path = svg.append("g").selectAll("path")
                  .data(data.connect)
                  .enter().append("path")
                  .attr("class", "link")
                  .style("stroke", function(d) { return d3.rgb(119, 136, 153); })
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
                               if(data["settings"][d.id] != undefined && !resetLocation) {
                                 if(data["settings"][d.id]["name"] != undefined) { return data["settings"][d.id]["name"]; }
                                 else { return d.id; }
                               }
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
                  if(data["settings"][d.source.id]["x"] != undefined && data["settings"][d.source.id]["y"] != undefined && !resetLocation) {
                      var dx_source = data["settings"][d.source.id]["x"];
                      var dy_source = data["settings"][d.source.id]["y"];
                      d.source.x = data["settings"][d.source.id]["x"];
                      d.source.y = data["settings"][d.source.id]["y"];
                  }
                  else {
                      var dx_source = d.source.x;
                      var dy_source = d.source.y;
                  }
              }
              else {
                  var dx_source = d.source.x;
                  var dy_source = d.source.y;
              }

              if(data["settings"][d.target.id] != undefined) {
                  if(data["settings"][d.target.id]["x"] != undefined && data["settings"][d.target.id]["y"] != undefined && !resetLocation) {
                      var dx_target = data["settings"][d.target.id]["x"];
                      var dy_target = data["settings"][d.target.id]["y"];
                      d.target.x = data["settings"][d.target.id]["x"];
                      d.target.y = data["settings"][d.target.id]["y"];
                  }
                  else {
                      var dx_target = d.target.x;
                      var dy_target = d.target.y;
                  }
              }
              else {
                  var dx_target = d.target.x;
                  var dy_target = d.target.y;
              }

              return "M" + dx_source + "," + dy_source + "A" + 0 + "," + 0 + " 0 0,1 " + dx_target + "," + dy_target;
      });

      node
          .attr("cx", function(d) {
              if(data["settings"][d.id] != undefined && !resetLocation) {
                  if(data["settings"][d.id]["x"] != undefined) {
                    d.x = data["settings"][d.id]["x"];
                    return d.x;
                  }
                  else { return d.x; }
              }
              else { return d.x; } })
          .attr("cy", function(d) {
              if(data["settings"][d.id] != undefined && !resetLocation) {
                  if(data["settings"][d.id]["y"] != undefined) {
                    d.y = data["settings"][d.id]["y"];
                    return d.y;
                  }
                  else { return d.y; }
              }
              else { return d.y; } });

      switchLabel
          .attr("transform", function(d) {
              if(data["settings"][d.id] != undefined && !resetLocation) {
                  if(data["settings"][d.id]["x"] != undefined && data["settings"][d.id]["y"] != undefined) { return 'translate(' + [data["settings"][d.id]["x"]-13, data["settings"][d.id]["y"]-10] + ')'; }
                  else { return 'translate(' + [d.x, d.y] + ')'; }
              }
              else { return 'translate(' + [d.x-13, d.y-10] + ')'; } });
    }

    function dragstarted(d) {
        // force.stop()
    }

    function dragged(d) {
        d.px += d3.event.dx;
        d.py += d3.event.dy;
        d.x += d3.event.dx;
        d.y += d3.event.dy;
        if(data["settings"][d.id] != undefined && !resetLocation) {
          data["settings"][d.id]["x"] += d3.event.dx;
          data["settings"][d.id]["y"] += d3.event.dy;
        }
        ticked();
    }

    function dragended(d) {
        d.fixed = true;
        ticked();
        // force.resume();
    }

    function mouseClick(d) {
        var tempTable = document.getElementById("initialText");
        tempTable.textContent = "";

        var loadLabel = document.getElementById("switch");
        loadLabel.textContent = "Loading...";

        var table = $("<table/>").addClass('table');
        $(document.getElementById("portTable")).html(table);
        $(document.getElementById("flowTable")).html(table);

        document.getElementById("flowTableHead").textContent = "";
        document.getElementById("portTableHead").textContent = "";
        document.getElementById("currentTime").textContent = "";

        currentSelectSwitch = d.id;
        isSelected = true;
        getNewSwitchData(data, d.id);
    }
}

function showFlowTable(container, data) {
    var showTime = document.getElementById("currentTime");
    var currentTime = new Date(Date.now());
    showTime.textContent = "Time : " + currentTime.toString();

    var showSwitch = document.getElementById("switch");
    showSwitch.textContent = "";

    var table = $("<table/>").addClass('table table-hover');
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
    var showHeader = document.getElementById("flowTableHead");
    showHeader.textContent = "Flow Table";

    var showTime = document.getElementById("currentTime");
    var currentTime = new Date(Date.now());
    showTime.textContent = "Time : " + currentTime.toString();

    var table = $("<table/>").addClass('table table-hover');
    var head = $("<thead/>");
    var row = $("<tr/>");
    // row.append($("<th/>").text("Switch ID"));
    row.append($("<th/>").text("Match"));
    row.append($("<th/>").text("Actions"));
    // row.append($("<th/>").text("Expire"));
    head.append(row);
    table.append(head);

    var body = $("<tbody/>");
    var hasFlow = false;
    $.each(data["flowmods"][switch_id], function(rowIndex, r) {
        var isActive = false;

        if(r["hard_timeout"] != 0) {
            var expireMillisec = Date.parse(r["timestamp"]) + (r["hard_timeout"] * 1000);
            var expireTime = new Date(expireMillisec);
            if(expireTime > Date.now()) {
              isActive = true;
              hasFlow = true;
            }
        }
        else if(r["hard_timeout"] == 0 && r["idle_timeout"] != 0) {
            var expireMillisec = Date.parse(r["timestamp"]) + ((r["idle_timeout"] + 1000) * 1000);
            var expireTime = new Date(expireMillisec);
            if(expireTime > Date.now()) {
              isActive = true;
              hasFlow = true;
            }
        }
        else if(r["hard_timeout"] == 0 && r["idle_timeout"] == 0) {
            isActive = true;
            hasFlow = true;
        }

        if(isActive) {
            var row = $("<tr/>");
            // row.append($("<td/>").text(r["switch_id"]));

            var match = $("<td/>");
            match.append($("<li/>").text("Wildcard : " + r["match"]["wildcards"] + "\n"));
            if(r["match"]["in_port"] != "0") { match.append($("<li/>").text("Switch Input Port : " + r["match"]["in_port"] + "\n")); }
            if(r["match"]["dl_src"] != "00:00:00:00:00:00" ) { match.append($("<li/>").text("Source MAC Address : " + r["match"]["dl_src"] + "\n")); }
            if(r["match"]["dl_dst"] != "00:00:00:00:00:00" ) { match.append($("<li/>").text("Destination MAC Address : " + r["match"]["dl_dst"] + "\n")); }
            if(r["match"]["dl_vlan"] != "0") { match.append($("<li/>").text("VLAN ID : " + r["match"]["dl_vlan"] + "\n")); }
            if(r["match"]["dl_vlan_pcp"] != "0") { match.append($("<li/>").text("VLAN Priority : " + r["match"]["dl_vlan_pcp"] + "\n")); }
            if(r["match"]["dl_type"] != "0") { match.append($("<li/>").text("Ethernet Frame Type : " + r["match"]["dl_type"] + "\n")); }
            if(r["match"]["nw_tos"] != "0") { match.append($("<li/>").text("IP ToS : " + r["match"]["nw_tos"] + "\n")); }
            if(r["match"]["nw_proto"] != "0") { match.append($("<li/>").text("IP Protocol : " + r["match"]["nw_proto"] + "\n")); }
            if(r["match"]["nw_src"] != "0.0.0.0") { match.append($("<li/>").text("Source IP Address : " + r["match"]["nw_src"] + "\n")); }
            if(r["match"]["nw_dst"] != "0.0.0.0") { match.append($("<li/>").text("Destination IP Address : " + r["match"]["nw_dst"] + "\n")); }
            if(r["match"]["tp_src"] != "0") { match.append($("<li/>").text("Source TCP/UDP Port : " + r["match"]["tp_src"] + "\n")); }
            if(r["match"]["tp_dst"] != "0") { match.append($("<li/>").text("Destination TCP/UDP Port : " + r["match"]["tp_dst"] + "\n")); }
            match.append($("<li/>").text("Idle Timeout : " + r["idle_timeout"]));
            match.append($("<li/>").text("Hard Timeout : " + r["hard_timeout"]));
            row.append(match);

            var action = $("<td/>");
            if(r["actions"][0]["type"] == 0) { action.append($("<li/>").text("Type : " + r["actions"][0]["type"] + " (OFPActionOutput)" + "\n")); }
            else { action.append($("<li/>").text("Type : " + r["actions"][0]["type"] + "\n")); }
            action.append($("<li/>").text("Switch Output Port : " + r["actions"][0]["port"] + "\n"));
            action.append($("<li/>").text("Max Length : " + r["actions"][0]["max_len"] + "\n"));
            row.append(action);

            // row.append($("<td/>").text(expireTime.toString()));
            body.append(row);
        }
    });
    table.append(body);

    var showStatus = document.getElementById("showStatus");
    if(hasFlow) {
      showStatus.textContent = "";
      return container.html(table);
    }
    else {
      showStatus.textContent = "No flow in this switch.";
    }
}

function showSwitchPort(container, data, switch_id) {
    var showHeader = document.getElementById("portTableHead");
    showHeader.textContent = "Switch Detail";

    var showSwitch = document.getElementById("switch");
    if(data["settings"][switch_id] != undefined) {
        if(data["settings"][switch_id]["name"] != undefined) { showSwitch.textContent = "Switch ID : " + switch_id + " (" + data["settings"][switch_id]["name"] + ")"; }
        else { showSwitch.textContent = "Switch ID : " + switch_id; }
    }
    else {
        showSwitch.textContent = "Switch ID : " + switch_id;
    }

    var table = $("<table/>").addClass('table table-hover');
    var head = $("<thead/>");
    var row = $("<tr/>");
    row.append($("<th/>").text("Port"));
    row.append($("<th/>").text("MAC Address"));
    head.append(row);
    table.append(head);

    var body = $("<tbody/>");
    var temp = 0
    $.each(data["switch_mac"][switch_id]["ports"], function(rowIndex, r) {
        var row = $("<tr/>").addClass('accordion-toggle');
        row.attr('data-toggle', 'collapse');
        row.attr('data-target', '#port'+temp);
        row.append($("<td/>").text(r["port_no"]));
        row.append($("<td/>").text(r["hw_addr"]));
        body.append(row);

        var rowInfo = $("<tr/>");
        var portInfo = $("<td/>").attr('colspan', 2);
        var collapseDiv = $("<div/>").addClass('accordion-body collapse hiddenRow');
        var portInfoTable = $("<table/>").addClass('table table-hover');
        var row = $("<tr/>");

        var column = $("<td/>");
        column.append($("<li/>").text("Received packets : " + data["ports"][switch_id][r["port_no"]]["rx_packets"] + "\n"));
        column.append($("<li/>").text("Transmitted packets : " + data["ports"][switch_id][r["port_no"]]["tx_packets"] + "\n"));
        column.append($("<li/>").text("Received bytes : " + data["ports"][switch_id][r["port_no"]]["rx_bytes"] + "\n"));
        column.append($("<li/>").text("Transmitted bytes : " + data["ports"][switch_id][r["port_no"]]["tx_bytes"] + "\n"));
        column.append($("<li/>").text("Packets dropped by RX : " + data["ports"][switch_id][r["port_no"]]["rx_dropped"] + "\n"));
        column.append($("<li/>").text("Packets dropped by TX : " + data["ports"][switch_id][r["port_no"]]["tx_dropped"] + "\n"));
        row.append(column);

        var column = $("<td/>");
        column.append($("<li/>").text("Receive errors : " + data["ports"][switch_id][r["port_no"]]["rx_errors"] + "\n"));
        column.append($("<li/>").text("Transmit errors : " + data["ports"][switch_id][r["port_no"]]["tx_errors"] + "\n"));
        column.append($("<li/>").text("Frame alignment errors : " + data["ports"][switch_id][r["port_no"]]["rx_frame_err"] + "\n"));
        column.append($("<li/>").text("Packet with RX overrun : " + data["ports"][switch_id][r["port_no"]]["rx_over_err"] + "\n"));
        column.append($("<li/>").text("CRC errors : " + data["ports"][switch_id][r["port_no"]]["rx_crc_err"] + "\n"));
        column.append($("<li/>").text("Collisions : " + data["ports"][switch_id][r["port_no"]]["collisions"] + "\n"));
        row.append(column);

        portInfoTable.append(row);
        collapseDiv.attr('id', 'port'+temp);
        collapseDiv.append(portInfoTable)
        portInfo.append(collapseDiv);
        rowInfo.append(portInfo);
        body.append(portInfo);

        temp++;
    });
    table.append(body);

    return container.html(table);
}

function sendDataToServer() {
    // console.log(document.getElementById("timeSlider").value);
    $.get('/dataquery', { timeSecond : document.getElementById("timeSlider").value })
    .success(function(res){
        data["switch"] = res["topology"]["node"];
        data["connect"] = res["topology"]["link"];
        data["switchCounter"] = res["topology"]["nodeCounter"];
        data["flowmods"] = res["flowTable"];
        data["switch_mac"] = res["switch"];
        data["ports"] = res["ports"];

        console.log(data);
        $("#topology").empty();
        visualize();

        if(isSelected) {
          getNewSwitchData(data, currentSelectSwitch);
        }
      })
    .error(function(err){ console.log(err); });
}

function timeUpdate(value) {
    var selectTime = new Date(parseInt(value))
    // console.log(selectTime);
    document.getElementById("showTime").textContent = selectTime;
}

function sendNodeLocation() {
  // var switchNode = data["switch"];
  var switchNode = [];
  for(var i = 0; i < data["switch"].length; i++) {
    var temp = {};
    temp["id"] = data["switch"][i]["id"];
    temp["x"] = data["switch"][i]["x"];
    temp["y"] = data["switch"][i]["y"];
    switchNode.push(temp);
  }

  $.get('/savenode', { switchNode : switchNode })
  .success(function(res){
      getData();
    })
  .error(function(err){
      console.log(err);
      getData();
  });
}

function resetTopo() {
  resetLocation = true;
  $("#topology").empty();
  visualize();
}
