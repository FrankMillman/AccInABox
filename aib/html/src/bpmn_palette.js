NS='http://www.w3.org/2000/svg';

// global variables to handle 'new connector'
waiting_for_source = null;
waiting_for_target = null;
waiting_for_anchor = null;

setup_bpmn_palette = function(palette, svg) {

  // don't delete the following lines yet
  // a similar approach will be required when implementing 'tabs' for multiple processes

  // var page = svg.parentNode;
  // var button_row = page.childNodes[page.childNodes.length-2];  // last child is help_msg
  // var palette = document.createElementNS(NS, 'svg');
  // palette.setAttributeNS(null, 'width', '900px');
  // palette.setAttributeNS(null, 'height', button_row.offsetHeight + 'px');
  // palette.style.cssFloat = 'left';
  // button_row.insertBefore(palette, button_row.firstChild);

  ////////////
  //  Task  //
  ////////////
  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  var path_data = 'M3,2 L46,2 L46,32 L3,32 Z';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Task';
  path.appendChild(title);
  path.onclick = function(e) {task_clicked(svg)};

  var task = document.createElementNS(NS, 'rect');
  palette.appendChild(task);
  task.svg = svg;
  task.setAttributeNS(null, 'x', 9);
  task.setAttributeNS(null, 'y', 7);
  task.setAttributeNS(null, 'width', 30);
  task.setAttributeNS(null, 'height', 20);
  task.setAttributeNS(null, 'rx', 3);
  task.setAttributeNS(null, 'ry', 3);
  task.setAttributeNS(null, 'stroke', 'black');
  task.setAttributeNS(null, 'stroke-width', 1);
  task.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Task';
  task.appendChild(title);
  task.onmouseup = function(e) {task_clicked(svg)};

  var task_clicked = function(svg) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Drag outline to required position';
    var rect = document.createElementNS(NS, 'rect')
    svg.appendChild(rect);
    rect.shape_type = 'task';
    rect.setAttributeNS(null, 'width', 90);
    rect.setAttributeNS(null, 'height', 70);
    rect.setAttributeNS(null, 'rx', 10);
    rect.setAttributeNS(null, 'ry', 10);
    rect.setAttributeNS(null, 'stroke', 'grey');
    rect.setAttributeNS(null, 'stroke-width', 1);
    rect.setAttributeNS(null, 'stroke-dasharray', '5, 5');
    rect.setAttributeNS(null, 'fill', 'transparent');
    rect.setAttributeNS(null, 'transform', 'translate(10, 10)');
    Drag.init(rect, 10, 10, 90, 70);
    };

  /////////////
  //  Event  //
  /////////////
  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  // var path_data = 'M75,2 L125,2 L125,32 L75,32'
  var path_data = 'M3,32 L3,62 L46,62 L46,32';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Event';
  path.appendChild(title);
  path.onclick = function(e) {event_clicked(svg)};

  var event = document.createElementNS(NS, 'circle');
  palette.appendChild(event);
  event.svg = svg;
  event.setAttributeNS(null, 'r', 10);
  event.setAttributeNS(null, 'cx', 24);
  event.setAttributeNS(null, 'cy', 47);
  event.setAttributeNS(null, 'stroke', 'black');
  event.setAttributeNS(null, 'stroke-width', 1);
  event.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Event';
  event.appendChild(title);
  event.onmouseup = function(e) {event_clicked(svg)};

  var event_clicked = function(svg) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Drag outline to required position';
    var circle = document.createElementNS(NS, 'circle')
    svg.appendChild(circle);
    circle.shape_type = 'event';
    circle.setAttributeNS(null, 'cx', 15);
    circle.setAttributeNS(null, 'cy', 15);
    circle.setAttributeNS(null, 'r', 15);
    circle.setAttributeNS(null, 'stroke', 'black');
    circle.setAttributeNS(null, 'stroke-width', 2);
    circle.setAttributeNS(null, 'stroke-dasharray', '5, 5');
    circle.setAttributeNS(null, 'fill', 'transparent');
    circle.setAttributeNS(null, 'transform', 'translate(10, 32)');
    Drag.init(circle, 10, 32, 30, 30);
    };

  ///////////////
  //  Gateway  //
  ///////////////
  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  var path_data = 'M3,62 L3,92 L46,92 L46,62';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Gateway';
  path.appendChild(title);
  path.onclick = function(e) {gateway_clicked(svg)};

  var gateway = document.createElementNS(NS, 'path');
  palette.appendChild(gateway);
  gateway.svg = svg;
  gateway.setAttributeNS(null, 'd', 'M24,68 L14,78 L24,88 L34,78 Z');
  gateway.setAttributeNS(null, 'stroke', 'black');
  gateway.setAttributeNS(null, 'stroke-width', 1);
  gateway.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Gateway';
  gateway.appendChild(title);
  gateway.onmouseup = function(e) {gateway_clicked(svg)};

  var gateway_clicked = function(svg) {
    var page = svg.parentNode;
    // alert('GATEWAY CLICKED');
    page.lastChild.firstChild.data = 'Drag outline to required position';
    var path = document.createElementNS(NS, 'path')
    svg.appendChild(path);
    path.shape_type = 'gateway';
    path.setAttributeNS(null, 'd', 'M 20 0 L 0 20 L 20 40 L 40 20 Z');
    path.setAttributeNS(null, 'stroke', 'black');
    path.setAttributeNS(null, 'stroke-width', 1);
    path.setAttributeNS(null, 'stroke-dasharray', '5, 5');
    path.setAttributeNS(null, 'fill', 'transparent');
    path.setAttributeNS(null, 'transform', 'translate(10, 64)');
    Drag.init(path, 10, 64, 40, 40);
    };

  /////////////////
  //  Connector  //
  /////////////////
  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  var path_data = 'M3,92 L3,122 L46,122 L46,92';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Connector';
  path.appendChild(title);
  path.onclick = function(e) {connector_clicked(svg)};

  var connector = document.createElementNS(NS, 'path');
  palette.appendChild(connector);
  connector.svg = svg;
  // connector.setAttributeNS(null, 'd', 'M 185 18 L 210 18');
  connector.setAttributeNS(null, 'd', 'M11,108 L34,108');
  connector.setAttributeNS(null, 'stroke', 'black');
  connector.setAttributeNS(null, 'stroke-width', 1);
  connector.setAttributeNS(null, 'fill', 'transparent');
  connector.setAttributeNS(null, 'marker-end', 'url(#arrow)');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Connector';
  connector.appendChild(title);
  connector.onmouseup = function(e) {connector_clicked(svg)};

  var connector_clicked = function(svg) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Step 1: click source shape';
    waiting_for_source = [svg, source_clicked];
    };

  var source_clicked = function(svg, source) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Step 2: click start point';

    var rect = document.createElementNS(NS, 'rect');
    svg.appendChild(rect);
    rect.setAttributeNS(null, 'width', source.bounds.w);
    rect.setAttributeNS(null, 'height', source.bounds.h);
    rect.setAttributeNS(null, 'x', source.bounds.x);
    rect.setAttributeNS(null, 'y', source.bounds.y);
    rect.setAttributeNS(null, 'stroke', 'blue');
    rect.setAttributeNS(null, 'stroke-width', 0.5);
    rect.setAttributeNS(null, 'fill', 'transparent');

    var top = document.createElementNS(NS, 'use');
    svg.appendChild(top);
    top.setAttributeNS(null, 'href', '#anchor');
    top.setAttributeNS(null, 'x', (source.bounds.x + (source.bounds.w/2) - 4));
    top.setAttributeNS(null, 'y', source.bounds.y - 4);
    top.onclick = function(e) {source_anchor_clicked(svg, source,
        ['top', source.bounds.x + (source.bounds.w/2), source.bounds.y])};

    var left = document.createElementNS(NS, 'use');
    svg.appendChild(left);
    left.setAttributeNS(null, 'href', '#anchor');
    left.setAttributeNS(null, 'x', (source.bounds.x - 4));
    left.setAttributeNS(null, 'y', source.bounds.y + (source.bounds.h/2) - 4);
    left.onclick = function(e) {source_anchor_clicked(svg, source,
        ['left', source.bounds.x, source.bounds.y  + (source.bounds.h/2)])};

    var right = document.createElementNS(NS, 'use');
    svg.appendChild(right);
    right.setAttributeNS(null, 'href', '#anchor');
    right.setAttributeNS(null, 'x', (source.bounds.x + source.bounds.w - 4));
    right.setAttributeNS(null, 'y', source.bounds.y + (source.bounds.h/2) - 4);
    right.onclick = function(e) {source_anchor_clicked(svg, source,
        ['right', source.bounds.x + source.bounds.w, source.bounds.y + (source.bounds.h/2)])};

    var bot = document.createElementNS(NS, 'use');
    svg.appendChild(bot);
    bot.setAttributeNS(null, 'href', '#anchor');
    bot.setAttributeNS(null, 'x', (source.bounds.x + (source.bounds.w/2) - 4));
    bot.setAttributeNS(null, 'y', source.bounds.y + source.bounds.h - 4);
    bot.onclick = function(e) {source_anchor_clicked(svg, source,
        ['bot', source.bounds.x + (source.bounds.w/2), source.bounds.y + source.bounds.h])};

    waiting_for_source = null;
    };

  var source_anchor_clicked = function(svg, source, source_anchor) {
    var exists = null;
    for (j=0; j<source.out_edges.length; j++) {
      var edge_id = source.out_edges[j];
      var edge = document.getElementById(edge_id);
      if (source_anchor[1] == edge.points[0][0] && source_anchor[2] == edge.points[0][1]) {
        exists = edge_id;
        break;
        };
      };
    if (exists !== null) {
      for (var x=0; x<5; x++) {svg.removeChild(svg.lastChild)};
      var page = svg.parentNode;
      page.lastChild.firstChild.data = '\xa0';

      var edge = document.getElementById(exists);
      var args = [null, edge.id, 'Exists - select option',
        ['Edit', 'Delete', 'Cancel'], 'Edit', 'Cancel', [edge, edge.on_question_return]];
      ask_question(args);
      return;
      };

    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Step 3: click target shape';

    for (var x=0; x<4; x++) {
      var last_child = svg.lastChild;
      if (x===0 && source_anchor[0]==='bot' || x===1 && source_anchor[0]==='right' ||
          x===2 && source_anchor[0]==='left' || x===3 && source_anchor[0]==='top')
        var keep_child = last_child;
      svg.removeChild(last_child)
      };
    svg.appendChild(keep_child);
    waiting_for_target = [svg, source, source_anchor, target_clicked];
  };

  var target_clicked = function(svg, source, source_anchor, target) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Step 4: click end point';

    var rect = document.createElementNS(NS, 'rect');
    svg.appendChild(rect);
    rect.setAttributeNS(null, 'width', target.bounds.w);
    rect.setAttributeNS(null, 'height', target.bounds.h);
    rect.setAttributeNS(null, 'x', target.bounds.x);
    rect.setAttributeNS(null, 'y', target.bounds.y);
    rect.setAttributeNS(null, 'stroke', 'blue');
    rect.setAttributeNS(null, 'stroke-width', 0.5);
    rect.setAttributeNS(null, 'fill', 'transparent');

    var top = document.createElementNS(NS, 'use');
    svg.appendChild(top);
    top.setAttributeNS(null, 'href', '#anchor');
    top.setAttributeNS(null, 'x', (target.bounds.x + (target.bounds.w/2) - 4));
    top.setAttributeNS(null, 'y', target.bounds.y - 4);
    top.onclick = function(e) {target_anchor_clicked(svg, source, source_anchor, target,
        ['top', target.bounds.x + (target.bounds.w/2), target.bounds.y])};

    var left = document.createElementNS(NS, 'use');
    svg.appendChild(left);
    left.setAttributeNS(null, 'href', '#anchor');
    left.setAttributeNS(null, 'x', (target.bounds.x - 4));
    left.setAttributeNS(null, 'y', target.bounds.y + (target.bounds.h/2) - 4);
    left.onclick = function(e) {target_anchor_clicked(svg, source, source_anchor, target,
        ['left', target.bounds.x, target.bounds.y  + (target.bounds.h/2)])};

    var right = document.createElementNS(NS, 'use');
    svg.appendChild(right);
    right.setAttributeNS(null, 'href', '#anchor');
    right.setAttributeNS(null, 'x', (target.bounds.x + target.bounds.w - 4));
    right.setAttributeNS(null, 'y', target.bounds.y + (target.bounds.h/2) - 4);
    right.onclick = function(e) {target_anchor_clicked(svg, source, source_anchor, target,
        ['right', target.bounds.x + target.bounds.w, target.bounds.y + (target.bounds.h/2)])};

    var bot = document.createElementNS(NS, 'use');
    svg.appendChild(bot);
    bot.setAttributeNS(null, 'href', '#anchor');
    bot.setAttributeNS(null, 'x', (target.bounds.x + (target.bounds.w/2) - 4));
    bot.setAttributeNS(null, 'y', target.bounds.y + target.bounds.h - 4);
    bot.onclick = function(e) {target_anchor_clicked(svg, source, source_anchor, target,
        ['bot', target.bounds.x + (target.bounds.w/2), target.bounds.y + target.bounds.h])};

    waiting_for_target = null;
    };

  var target_anchor_clicked = function(svg, source, source_anchor, target, target_anchor) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = '\xa0';
    for (var x=0; x<7; x++) {svg.removeChild(svg.lastChild)};

    var [source_anchor, source_x, source_y] = source_anchor;
    var [target_anchor, target_x, target_y] = target_anchor;
    var new_points = [[source_x, source_y]]
    if (target_x !== source_x && target_y !== source_y) {  // else straight line
      // not every permutation catered for - add as required
      if (source_anchor==='top') {
        if (target_anchor==='bot') {
          new_points.push([source_x, target_y + (source_y-target_y)/2]);
          new_points.push([target_x, target_y + (source_y-target_y)/2]);
          }
        else {
          new_points.push([source_x, target_y]);
          }
        }
      else if (source_anchor==='left') {
        if (target_anchor==='right') {
          new_points.push([target_x - (source_x-target_x)/2, source_y]);
          new_points.push([target_x - (source_x-target_x)/2, target_y]);
          }
        else {
          new_points.push([target_x, source_y]);
          }
        }
      else if (source_anchor==='right') {
        if (target_anchor==='left') {
          new_points.push([target_x - (target_x-source_x)/2, source_y]);
          new_points.push([target_x - (target_x-source_x)/2, target_y]);
          }
        else {
          new_points.push([target_x, source_y]);
          }
        }
      else if (source_anchor==='bot') {
        if (target_anchor==='top') {
          new_points.push([source_x, source_y + (target_y-source_y)/2]);
          new_points.push([target_x, source_y + (target_y-source_y)/2]);
          }
        else {
          new_points.push([source_x, target_y]);
          }
        }
      };
    new_points.push([target_x, target_y])

    var g = document.createElementNS(NS, 'g')
    svg.appendChild(g);
    g.points = new_points;
    build_connector(g, new_points);

    var args = [svg.ref, 'connector', 'New', [source.id, target.id, new_points]];
    send_request('clicked', args);
    };

  ///////////////////
  //  Sub-process  //
  ///////////////////
  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  var path_data = 'M3,122 L3,152 L46,152 L46,122';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Sub-process';
  path.appendChild(title);
  path.onclick = function(e) {subprocess_clicked(svg)};

  var subprocess = document.createElementNS(NS, 'rect');
  palette.appendChild(subprocess);
  subprocess.svg = svg;
  subprocess.setAttributeNS(null, 'x', 9);  //235);
  subprocess.setAttributeNS(null, 'y', 127);  //7);
  subprocess.setAttributeNS(null, 'width', 30);
  subprocess.setAttributeNS(null, 'height', 20);
  subprocess.setAttributeNS(null, 'rx', 3);
  subprocess.setAttributeNS(null, 'ry', 3);
  subprocess.setAttributeNS(null, 'stroke', 'black');
  subprocess.setAttributeNS(null, 'stroke-width', 1);
  subprocess.setAttributeNS(null, 'stroke-dasharray', '2, 2');
  subprocess.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Sub-process';
  subprocess.appendChild(title);
  subprocess.onmouseup = function(e) {subprocess_clicked(svg)};

  var subprocess_clicked = function(svg) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Click top-left, drag to bottom-right';
    svg.select_subprocess = [subprocess_selected];
    svg.onmousedown = svg.subprocess_start;
    svg.onmousemove = svg.subprocess_drag;
    svg.onmouseup = svg.subprocess_done;
    };

  var subprocess_selected = function(svg, start_x, start_y, end_x, end_y) {
    svg.select_subprocess = null;
    svg.onmousedown = null;
    svg.onmousemove = null;
    svg.onmouseup = null;
    var page = svg.parentNode;
    page.lastChild.firstChild.data = '\xa0';
    var args = [svg.ref, null, 'Sub', [start_x, start_y, end_x, end_y]];
    send_request('clicked', args);
    };

  ////////////////////////
  //  Add/remove space  //
  ////////////////////////
  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  var path_data = 'M3,152 L3,182 L46,182 L46,152';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Add/remove space to the right';
  path.appendChild(title);
  path.onclick = function(e) {addspace_clicked(svg, false)};

  var addright = document.createElementNS(NS, 'path');
  palette.appendChild(addright);
  addright.svg = svg;
  addright.setAttributeNS(null, 'd', 'M11,167 L34,167');
  addright.setAttributeNS(null, 'stroke', 'black');
  addright.setAttributeNS(null, 'stroke-width', 1);
  addright.setAttributeNS(null, 'stroke-dasharray', '4, 4');
  addright.setAttributeNS(null, 'fill', 'transparent');
  var addrightarrow = document.createElementNS(NS, 'path');
  palette.appendChild(addrightarrow);
  addrightarrow.svg = svg;
  addrightarrow.setAttributeNS(null, 'd', 'M30,162 L34,167 L30,172');
  addrightarrow.setAttributeNS(null, 'stroke', 'black');
  addrightarrow.setAttributeNS(null, 'stroke-width', 1);
  addrightarrow.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Add/remove space to the right';
  addright.appendChild(title);
  addright.onmouseup = function(e) {addspace_clicked(svg, false)};

  var path = document.createElementNS(NS, 'path');
  palette.appendChild(path);
  var path_data = 'M3,182 L3,212 L46,212 L46,182';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'grey');
  path.setAttributeNS(null, 'stroke-width', 0.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Add/remove space to the left';
  path.appendChild(title);
  path.onclick = function(e) {addspace_clicked(svg, true)};

  var addleft = document.createElementNS(NS, 'path');
  palette.appendChild(addleft);
  addleft.svg = svg;
  addleft.setAttributeNS(null, 'd', 'M11,197 L34,197');
  addleft.setAttributeNS(null, 'stroke', 'black');
  addleft.setAttributeNS(null, 'stroke-width', 1);
  addleft.setAttributeNS(null, 'stroke-dasharray', '4, 4');
  addleft.setAttributeNS(null, 'fill', 'transparent');
  var addleftarrow = document.createElementNS(NS, 'path');
  palette.appendChild(addleftarrow);
  addleftarrow.svg = svg;
  addleftarrow.setAttributeNS(null, 'd', 'M13,192 L9,197 L13,202');
  addleftarrow.setAttributeNS(null, 'stroke', 'black');
  addleftarrow.setAttributeNS(null, 'stroke-width', 1);
  addleftarrow.setAttributeNS(null, 'fill', 'transparent');
  var title = document.createElementNS(NS, 'title');
  title.innerHTML = 'Add/remove space to the left';
  addleft.appendChild(title);
  addleft.onmouseup = function(e) {addspace_clicked(svg, true)};

  var addspace_clicked = function(svg, shift_left) {
    var page = svg.parentNode;
    page.lastChild.firstChild.data = 'Click start position, drag to increase/reduce space';
    svg.select_addspace = [addspace_selected, shift_left];
    svg.onmousedown = svg.addspace_start;
    svg.onmousemove = svg.addspace_drag;
    svg.onmouseup = svg.addspace_done;
    };

  var addspace_selected = function(svg, shift_left, start_x, end_x) {
    svg.select_addspace = null;
    svg.onmousedown = null;
    svg.onmousemove = null;
    svg.onmouseup = null;
    var page = svg.parentNode;
    page.lastChild.firstChild.data = '\xa0';
    if (start_x !== end_x) {
      var args = [svg.ref, null, 'AddSpace', [shift_left, start_x, end_x]];
      send_request('clicked', args);
      };
    };

  ///////////////////////////////////////
  //  Set up 'Drag' object for palette //
  ///////////////////////////////////////
  var Drag = {

    obj : null,

    init : function(o, x, y, w, h) {
      o.onmousedown = Drag.start;
      o.drag_bounds = [x, y, w, h];
      },

    start : function(e) {  // on mousedown
      if (e.button !== 0)  // 0 = left button
        return;
      var o = Drag.obj = this;
      o.dragged = false;  // to detect if dragged

      var svg = o.parentNode;
      var [minX, minY, maxX, maxY] = svg.get_bounds();
      var [x, y, w, h] = o.drag_bounds;
      maxX -= w;
      maxY -= h;

      o.minMouseX = e.clientX - x;
      o.maxMouseX = o.minMouseX + maxX - minX;

      o.minMouseY = e.clientY - y;
      o.maxMouseY = o.minMouseY + maxY - minY;

      document.onmousemove = Drag.drag;
      document.onmouseup = Drag.end;
      },

    drag : function(e) {
      var o = Drag.obj;
      o.dragged = true;

      var ex = e.clientX;
      var ey = e.clientY;

      ex = Math.max(ex, o.minMouseX);
      ex = Math.min(ex, o.maxMouseX);
      ey = Math.max(ey, o.minMouseY);
      ey = Math.min(ey, o.maxMouseY);

      o.posX = Math.round(ex - o.minMouseX);  // convert back to relative, ensure integer
      o.posY = Math.round(ey - o.minMouseY);

      o.setAttributeNS(null, 'transform', 'translate(' + o.posX + ', ' + o.posY + ')');
      },

    end : function() {
      var o = Drag.obj;

      document.onmousemove = null;
      document.onmouseup = null;
      Drag.obj = null;

      if (o.dragged) {
        var args = [o.parentNode.ref, o.shape_type, 'New', [o.posX, o.posY]];
        send_request('clicked', args);
        };

      var svg = o.parentNode;
      svg.removeChild(o);

      var page = svg.parentNode;
      page.lastChild.firstChild.data = '\xa0';  // remove help message
      },
    };

  };
