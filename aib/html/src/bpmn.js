NS='http://www.w3.org/2000/svg';

function setup_bpmn(frame, ref, nodes, edges) {
  var page = frame.page;
  page.style.padding = '0px';  // over-ride default padding

  var palette = document.createElementNS(NS, 'svg');
  page.appendChild(palette);
  palette.setAttributeNS(null, 'width', 50);
  palette.setAttributeNS(null, 'height', 500);

  var svg = document.createElementNS(NS, 'svg');
  page.appendChild(svg);
  svg.setAttributeNS(null, 'width', 1100);
  svg.setAttributeNS(null, 'height', 500);
  svg.style.margin = '2px';
  svg.style.border = '1px solid #7c7cea';
  svg.style.backgroundImage = 'url(' + iGrid_src + ')'
  svg.ref = ref;

  setup_bpmn_palette(palette, svg);
  setup_bpmn_defs(svg);
  render_bpmn(svg, nodes, edges);

  var form = frame.form;
  var max_x = (max_w - form.offsetWidth);
  var max_y = (max_h - form.offsetHeight);
  form.style.left = (max_x / 2) + 'px';
  form.style.top = (max_y / 4) + 'px';
  form.obj_dict[ref] = svg;

  svg.oncontextmenu = function(e) {
    return false;
    };
    svg.subprocess_start = function(e) {
      [this.min_x, this.min_y, this.max_x, this.max_y] = this.get_bounds();
      this.select_subprocess.push(e.clientX - this.min_x, e.clientY - this.min_y);
      var rubber_band = document.createElementNS(NS, 'rect');
      this.appendChild(rubber_band);
      rubber_band.setAttributeNS(null, 'x', e.clientX - this.min_x);
      rubber_band.setAttributeNS(null, 'y', e.clientY - this.min_y);
      rubber_band.setAttributeNS(null, 'width', 0);
      rubber_band.setAttributeNS(null, 'height', 0);
      rubber_band.setAttributeNS(null, 'stroke', 'grey');
      rubber_band.setAttributeNS(null, 'stroke-width', 1);
      rubber_band.setAttributeNS(null, 'stroke-dasharray', '3 3');
      rubber_band.setAttributeNS(null, 'fill', 'transparent');
      svg.onselectstart = function(){return false};  // disable text selection
    };
    svg.subprocess_drag = function(e) {
      var rubber_band = this.lastChild;
      var x = rubber_band.getAttributeNS(null, 'x');
      var y = rubber_band.getAttributeNS(null, 'y');
      rubber_band.setAttributeNS(null, 'width', e.clientX - this.min_x - x);
      rubber_band.setAttributeNS(null, 'height', e.clientY - this.min_y - y);
      };
    svg.subprocess_done = function(e) {
	  var x = Math.round(e.clientX);
	  var y = Math.round(e.clientY);
      // this.select_subprocess.push(e.clientX - this.min_x, e.clientY - this.min_y);
      this.select_subprocess.push(x - this.min_x, y - this.min_y);
      this.removeChild(this.lastChild);
      var subprocess_selected = this.select_subprocess.shift();  // extract first element
      subprocess_selected.call(this, this, ...this.select_subprocess);
      svg.onselectstart = null;  // restore text selection
      };

    svg.addspace_start = function(e) {
      [this.min_x, this.min_y, this.max_x, this.max_y] = this.get_bounds();
      this.select_addspace.push(e.clientX-this.min_x);
      var vert = document.createElementNS(NS, 'line');
      this.appendChild(vert);
      vert.setAttributeNS(null, 'x1', e.clientX-this.min_x);
      vert.setAttributeNS(null, 'y1', 0);
      vert.setAttributeNS(null, 'x2', e.clientX-this.min_x);
      vert.setAttributeNS(null, 'y2', this.max_y-this.min_y);
      vert.setAttributeNS(null, 'stroke', 'grey');
      vert.setAttributeNS(null, 'stroke-width', 1);
      vert.setAttributeNS(null, 'stroke-dasharray', '3 3');
      };
    svg.addspace_drag = function(e) {
      var vert = this.lastChild;
      vert.setAttributeNS(null, 'x1', e.clientX-this.min_x);
      vert.setAttributeNS(null, 'x2', e.clientX-this.min_x);
      };
    svg.addspace_done = function(e) {
      this.select_addspace.push(e.clientX-this.min_x);
      this.removeChild(this.lastChild);
      var addspace_selected = this.select_addspace.shift();  // extract first element
      addspace_selected.call(this, this, ...this.select_addspace);
      };

  };

function render_bpmn(svg, nodes, edges) {
  while (svg.childNodes.length > 1)  // do not remove 'defs'
    svg.removeChild(svg.lastChild);

    ////////////////////////////
    //  Set up 'Drag' object  //
    ////////////////////////////
    var Drag = {

    obj : null,

    init : function(o, x, y, w, h) {
      o.onmousedown = Drag.start;
      o.drag_bounds = [x, y, w, h];
      },

    start : function(e) {  // on mousedown
      if (e.button !== 0)  // 0 = left button
        return;
      if (waiting_for_source !== null || waiting_for_target !== null)  // let onclick handle this
        return;
      var o = Drag.obj = this;
      var svg = o.parentNode;
      var [minX, minY, maxX, maxY] = svg.get_bounds();
      var [x, y, w, h] = o.drag_bounds;
      maxX -= w;
      maxY -= h;
      var page = svg.parentNode;
      page.lastChild.firstChild.data = '\xa0';  // in case active

      o.dragged = false;  // to detect if dragged

      for (var j=0; j<o.in_edges.length; j++) {
        var edge_id = o.in_edges[j];
        var edge = document.getElementById(edge_id);
        edge.temp_points = edge.points;
        };

      for (var j=0; j<o.out_edges.length; j++) {
        var edge_id = o.out_edges[j];
        var edge = document.getElementById(edge_id);
        edge.temp_points = edge.points;
        };

      o.minMouseX = e.clientX - x;
      o.maxMouseX = o.minMouseX + maxX - minX;

      o.minMouseY = e.clientY - y;
      o.maxMouseY = o.minMouseY + maxY - minY;

      o.posX = x;
      o.posY = y;

      document.onmousemove  = Drag.drag;
      document.onmouseup    = Drag.end;
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

      var nx = Math.round(ex - o.minMouseX);  // convert back to relative, ensure integer
      var ny = Math.round(ey - o.minMouseY);

      o.setAttributeNS(null, 'transform', 'translate(' + nx + ', ' + ny + ')');

      for (var j=0; j<o.in_edges.length; j++) {
        var edge_id = o.in_edges[j];
        var edge = document.getElementById(edge_id);

        var pts = edge.points;
        if (pts[1][0] === pts[0][0])  // start vertical
          var start_anchor = (pts[1][1] > pts[0][1]) ? 'bottom' : 'top'
        else  // start horizontal
          var start_anchor = (pts[1][0] > pts[0][0]) ? 'right' : 'left'
        if (pts[pts.length-1][0] === pts[pts.length-2][0])  // end vertical
          var end_anchor = (pts[pts.length-2][1] > pts[pts.length-1][1]) ? 'bottom' : 'top'
        else  // end horizontal
          var end_anchor = (pts[pts.length-2][0] > pts[pts.length-1][0]) ? 'right' : 'left'

        var pts = edge.temp_points;
        var new_start = [pts[0][0], pts[0][1]];
        var new_end = [pts[pts.length-1][0] + (nx - o.posX), pts[pts.length-1][1] + (ny - o.posY)];

        var new_points = [new_start];
        switch (start_anchor) {  // not every permutation catered for - add as required
          case 'right':
            if (end_anchor === 'left' && new_end[1] != new_start[1] && new_end[0] > new_start[0]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_end[1]]);
              }
            else if (end_anchor === 'top' || end_anchor === 'bottom') {
              new_points.push([new_end[0], new_start[1]]);
              };
            break;
          case 'left':
            if (end_anchor === 'right' && new_end[1] != new_start[1] && new_end[0] > new_start[0]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_end[1]]);
              }
            else if (end_anchor === 'top' || end_anchor === 'bottom') {
              new_points.push([new_end[0], new_start[1]]);
              };
            break;
          case 'top':
            if (end_anchor === 'bottom' && new_end[0] != new_start[0] && new_end[1] > new_start[1]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_end[1]]);
              }
            else if (end_anchor === 'left' || end_anchor === 'right') {
              new_points.push([new_start[0], new_end[1]]);
              };
            break;
          case 'bottom':
            if (end_anchor === 'top' && new_end[0] != new_start[0] && new_end[1] > new_start[1]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_end[1]]);
              }
            else if (end_anchor === 'left' || end_anchor === 'right') {
              new_points.push([new_start[0], new_end[1]]);
              };
            break;
          };
        new_points.push(new_end);
        edge.removeChild(edge.lastChild);
        build_connector(edge, new_points);
        edge.temp_points = new_points;
        };

      for (var j=0; j<o.out_edges.length; j++) {
        var edge_id = o.out_edges[j];
        var edge = document.getElementById(edge_id);

        var pts = edge.points;
        if (pts[1][0] === pts[0][0])  // start vertical
          var start_anchor = (pts[1][1] > pts[0][1]) ? 'bottom' : 'top'
        else  // start horizontal
          var start_anchor = (pts[1][0] > pts[0][0]) ? 'right' : 'left'
        if (pts[pts.length-1][0] === pts[pts.length-2][0])  // end vertical
          var end_anchor = (pts[pts.length-2][1] > pts[pts.length-1][1]) ? 'bottom' : 'top'
        else  // end horizontal
          var end_anchor = (pts[pts.length-2][0] > pts[pts.length-1][0]) ? 'right' : 'left'

        var pts = edge.temp_points;
        var new_start = [pts[0][0] + (nx - o.posX), pts[0][1] + (ny - o.posY)];
        var new_end = [pts[pts.length-1][0], pts[pts.length-1][1]];

        var pts = edge.temp_points;
        var new_points = [new_start];
        switch (start_anchor) {  // not every permutation catered for - add as required
          case 'right':
            if (end_anchor === 'left' && new_end[1] != new_start[1] && new_end[0] > new_start[0]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_end[1]]);
              }
            else if (end_anchor === 'top' || end_anchor === 'bottom') {
              new_points.push([new_end[0], new_start[1]]);
              };
            break;
          case 'left':
            if (end_anchor === 'right' && new_end[1] != new_start[1] && new_end[0] > new_start[0]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_end[1]]);
              }
            else if (end_anchor === 'top' || end_anchor === 'bottom') {
              new_points.push([new_end[0], new_start[1]]);
              };
            break;
          case 'top':
            if (end_anchor === 'bottom' && new_end[0] != new_start[0] && new_end[1] > new_start[1]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              }
            else if (end_anchor === 'left' || end_anchor === 'right') {
              new_points.push([new_start[0], new_end[1]]);
              };
            break;
          case 'bottom':
            if (end_anchor === 'top' && new_end[0] != new_start[0] && new_end[1] > new_start[1]) {
              new_points.push([new_start[0] + Math.round((new_end[0]-new_start[0])/2), new_start[1]]);
              }
            else if (end_anchor === 'left' || end_anchor === 'right') {
              new_points.push([new_start[0], new_end[1]]);
              };
            break;
          };
        new_points.push(new_end);
        edge.removeChild(edge.lastChild);
        build_connector(edge, new_points);
        edge.temp_points = new_points;
        };

      o.posX = nx;
      o.posY = ny;
      },

    end : function() {

      var o = Drag.obj;

      document.onmousemove = null;
      document.onmouseup = null;
      Drag.obj = null;

      if (!o.dragged)  // no drag took place
        return;

      var in_edges = [];
      for (var j=0; j<o.in_edges.length; j++) {
        var edge_id = o.in_edges[j];
        var edge = document.getElementById(edge_id);
        edge.points = edge.temp_points;
        in_edges.push([edge_id, edge.points]);
        edge.temp_points = null;
        };

      var out_edges = [];
      for (var j=0; j<o.out_edges.length; j++) {
        var edge_id = o.out_edges[j];
        var edge = document.getElementById(edge_id);
        edge.points = edge.temp_points;
        out_edges.push([edge_id, edge.points]);
        edge.temp_points = null;
        };

      var args = [o.parentNode.ref, o.id, 'Move', [o.posX, o.posY, in_edges, out_edges]];
      send_request('clicked', args);
      },
    };

  svg.get_bounds = function() {
    var bounding_rect = this.getBoundingClientRect();
    return [bounding_rect.left, bounding_rect.top, bounding_rect.right-2, bounding_rect.bottom-2];
    };

  for (var i=0; i<nodes.length; i++) {
    var [node_type, node_args] = nodes[i];

    var shape = document.createElementNS(NS, 'g')
    svg.appendChild(shape);
    shape.id = node_args.elem_id;
    var title = document.createElementNS(NS, 'title');
    title.innerHTML = shape.id;
    shape.appendChild(title);
    var name = node_args.name;
    var bounds = node_args.bounds;
    var x=bounds.x, y=bounds.y, w=bounds.w, h=bounds.h;
    shape.setAttributeNS(null, 'transform', 'translate(' + x + ', ' + y + ')');
    shape.bounds = bounds;
    Drag.init(shape, x, y, w, h);
    shape.in_edges = node_args.in_edges;
    shape.out_edges = node_args.out_edges;
    shape.onclick = function(e) {
      if (waiting_for_anchor !== null)
        return false;
      if (waiting_for_source !== null) {
        var [svg, source_clicked] = waiting_for_source;
        source_clicked.call(this, svg, this);
        }
      else if (waiting_for_target !== null) {
        var [svg, source, source_anchor, target_clicked] = waiting_for_target;
        if (source !== this)
          target_clicked.call(this, svg, source, source_anchor, this);
        }
      };
    shape.oncontextmenu = function(e) {
      var args = [null, this.id, 'Select option',
        ['Edit', 'Delete', 'Cancel'], 'Edit', 'Cancel', [this, this.on_context_return]];
      ask_question(args);
      return false;
      };
    shape.on_context_return = function(answer) {
      if (answer === 'Cancel')
        return;
      if (answer === 'Edit') {
        var args = [this.parentNode.ref, this.id, 'Edit'];
        send_request('clicked', args);
        }
      else if (answer === 'Delete') {
        var args = [null, this.id, 'Ok to delete ' + this.id + '?',
          ['Cancel', 'Ok'], 'Cancel', 'Cancel', [this, this.on_confirm_delete]];
        ask_question(args);
        };
      };
    shape.on_confirm_delete = function(answer) {
      if (answer === 'Ok') {
        var args = [this.parentNode.ref, this.id, 'Delete'];
        send_request('clicked', args);
        };
      };

    switch(node_type) {
      case 'event':
        var event = document.createElementNS(NS, 'use');
        shape.appendChild(event);
        var event_types = {};
        event_types['startEvent'] = 'start';
        event_types['endEvent'] = 'end';
        event_types['intermediateCatchEvent'] = 'inter';
        event_types['intermediateThrowEvent'] = 'inter';
        event_types['boundaryEvent'] = 'boundary';
        event.setAttributeNS(null, 'href', '#' + event_types[node_args.event_type]);
        event.setAttributeNS(null, 'width', w);
        event.setAttributeNS(null, 'height', h);
        if (node_args.event_defn !== null) {
          var event_defn = document.createElementNS(NS, 'use');
          shape.appendChild(event_defn);
          event_defn.setAttributeNS(null, 'href', '#' + node_args.event_defn);
          event_defn.setAttributeNS(null, 'width', w);
          event_defn.setAttributeNS(null, 'height', h);
          };
        if (name !==null)  // create text node for name, with word-wrap
          word_wrap(shape, name, -10, h, w+30);  // name, parent, x, y, max_x
        break;
      case 'gateway':
        var gateway = document.createElementNS(NS, 'use');
        shape.appendChild(gateway);
        var gateway_types = {};
        gateway_types[null] = '#none_gw';
        gateway_types['exclusive'] = '#exclusive_gw';
        gateway_types['inclusive'] = '#inclusive_gw';
        gateway_types['parallel'] = '#parallel_gw';
        gateway.setAttributeNS(null, 'href', gateway_types[node_args.gateway_type]);
        gateway.setAttributeNS(null, 'width', w);
        gateway.setAttributeNS(null, 'height', h);
        if (name !== null)  // create text node for name, with word-wrap
          word_wrap(shape, name, -10, h, w+30);  // name, parent, x, y, max_x
        break;
      case 'task':
        var task = document.createElementNS(NS, 'use');
        var task_types = {};
        task_types[null] = '#none_task';
        task_types['user'] = '#user_task';
        task_types['recv'] = '#recv_task';
        task_types['send'] = '#send_task';
        task_types['script'] = '#script_task';
        task_types['service'] = '#service_task';
        shape.appendChild(task);
        task.setAttributeNS(null, 'href', task_types[node_args.task_type]);
        task.setAttributeNS(null, 'width', w);
        task.setAttributeNS(null, 'height', h);
        if (name !== null) {  // create text node for name, with word-wrap
          var x_pos = 5, y_pos = (node_args.task_type === null ? 8 : 20);
          word_wrap(shape, name, x_pos, y_pos, w-2);  // name, parent, x, y, max_x
          };
        break;
      case 'sub_proc':
        var sub_proc = document.createElementNS(NS, 'rect');
        shape.appendChild(sub_proc);
        sub_proc.setAttributeNS(null, 'width', w);
        sub_proc.setAttributeNS(null, 'height', h);
        sub_proc.setAttributeNS(null, 'rx', 10);
        sub_proc.setAttributeNS(null, 'ry', 10);
        sub_proc.setAttributeNS(null, 'stroke', 'black');
        sub_proc.setAttributeNS(null, 'stroke-width', 1);
        sub_proc.setAttributeNS(null, 'fill', 'transparent');
        break;
      };
    };

  for (var i=0; i<edges.length; i++) {
    var edge = edges[i];
    var g = document.createElementNS(NS, 'g')
    svg.appendChild(g);
    g.id = edge[1].edge_id;
    var points = edge[1].points;
    g.points = points;
    build_connector(g, points);
    // if (edge[1].name !==null)  // create text node for name, with word-wrap - where??
    //   debug(edge[1].name);
    g.on_question_return = function(answer) {
      if (answer === 'Cancel')
        return;
      if (answer === 'Edit') {
        var args = [this.parentNode.ref, this.id, 'Edit'];
        send_request('clicked', args);
        }
      else if (answer === 'Delete') {
        var args = [null, this.id, 'Ok to delete ' + this.id + '?',
          ['Cancel', 'Ok'], 'Cancel', 'Cancel', [this, this.on_confirm_delete]];
        ask_question(args);
        };
      };
    g.on_confirm_delete = function(answer) {
      if (answer === 'Ok') {
        var args = [this.parentNode.ref, this.id, 'Delete'];
        send_request('clicked', args);
        };
      };
    };

  };

/////////////////
//  Word wrap  //
/////////////////
function word_wrap(parent, name, x, y, max_x) {
  // crude algorithm for word-wrap - can be improved!
  // see BPMN2.0 spec Page 411 Section 12.3.1 for positioning of Labels
  var text = document.createElementNS(NS, 'text');
  parent.appendChild(text);
  text.setAttributeNS(null, 'x', x);
  text.setAttributeNS(null, 'y', y);
  text.setAttributeNS(null, 'font-size', 10);
  var words = name.split(' '), word_pos = 0;
  var temp_text = document.createElementNS(NS, 'text'), temp_string = words[word_pos];
  parent.append(temp_text);  // remove at end
  while (true) {
    word_pos += 1;
    if (word_pos === words.length) {
      var tspan = document.createElementNS(NS, 'tspan');
      text.appendChild(tspan);
      tspan.innerHTML = temp_string + '\n';
      tspan.setAttributeNS(null, 'x', x+5);
      tspan.setAttributeNS(null, 'dy', 10);
      break;
      };
    temp_text.innerHTML = temp_string + ' ' + words[word_pos];
    if (temp_text.getBBox().width >= max_x) {
      var tspan = document.createElementNS(NS, 'tspan');
      text.appendChild(tspan);
      tspan.innerHTML = temp_string + ' ';
      tspan.setAttributeNS(null, 'x', x+5);
      tspan.setAttributeNS(null, 'dy', 10);
      temp_string = words[word_pos];
      }
    else
      temp_string += ' ' + words[word_pos];
    };
  parent.removeChild(parent.lastChild);
  };

///////////////////////
//  Build Connector  //
///////////////////////
function build_connector(g, points) {
  var path_data = '';
  for (var j=0; j<points.length; j++) {
    var [x, y] = points[j];
    if (j === 0)
      path_data += 'M ' + x + ',' + y
    else if (j === (points.length-1)) {
      var px = points[j-1][0], py = points[j-1][1];  // previous xy
      // leave space for arrow - depends on line orientation and direction
      var spc = 9;
      if (y === py)
        x += (x > px) ? -spc : spc
      else if (x === px)
        y += (y > py) ? -spc : spc
      path_data += ' L ' + x + ',' + y;
      }
    else {
      var [px, py] = points[j-1];  // previous xy
      var [nx, ny] = points[j+1];  // next xy
      // if (px === x && x === nx)
      //   continue;
      // if (py === y && y === ny)
      //   continue;
      if (x < px)  // move left
        if (ny < y)  // then up
          path_data += ' L ' + (x+5) + ',' + y + ' S ' + x + ',' + y + ' ' + x + ',' + (y-5);
        else  // then down
          path_data += ' L ' + (x+5) + ',' + y + ' S ' + x + ',' + y + ' ' + x + ',' + (y+5);
      else if (x > px)  // move right
        if (ny < y)  // then up
          path_data += ' L ' + (x-5) + ',' + y + ' S ' + x + ',' + y + ' ' + x + ',' + (y-5);
        else  // then down
          path_data += ' L ' + (x-5) + ',' + y + ' S ' + x + ',' + y + ' ' + x + ',' + (y+5);
      else if (y < py)  // move up
        if (nx < x)  // then left
          path_data += ' L ' + x + ',' + (y+5) + ' S ' + x + ',' + y + ' ' + (x-5) + ',' + y;
        else  // then right
          path_data += ' L ' + x + ',' + (y+5) + ' S ' + x + ',' + y + ' ' + (x+5) + ',' + y;
      else if (y > py)  // move down
        if (nx < x)  // then left
          path_data += ' L ' + x + ',' + (y-5) + ' S ' + x + ',' + y + ' ' + (x-5) + ',' + y;
        else  // then right
          path_data += ' L ' + x + ',' + (y-5) + ' S ' + x + ',' + y + ' ' + (x+5) + ',' + y;
      };
    };
  var path = document.createElementNS(NS, 'path')
  g.appendChild(path);
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 1.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  path.setAttributeNS(null, 'marker-end', 'url(#arrow)');
  };
