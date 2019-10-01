NS='http://www.w3.org/2000/svg';

////////////////////////////////////////
//  Set up all definitions for reuse  //
////////////////////////////////////////
setup_bpmn_defs = function(svg) {
  var defs = document.createElementNS(NS, 'defs');
  svg.appendChild(defs);

  //////////////////////
  //  Arrow marker    //
  //////////////////////
  var marker = document.createElementNS(NS, 'marker');
  defs.appendChild(marker);
  marker.setAttributeNS(null, 'markerWidth', 7);
  marker.setAttributeNS(null, 'markerHeight', 7);
  marker.setAttributeNS(null, 'refX', 0);
  marker.setAttributeNS(null, 'refY', 3);
  marker.setAttributeNS(null, 'orient', 'auto');
  marker.setAttributeNS(null, 'markerUnits', 'strokeWidth');
  marker.id = 'arrow';
  var path = document.createElementNS(NS, 'path');
  marker.appendChild(path);
  path.setAttributeNS(null, 'd', 'M0,0 L0,6 L6,3 z');
  path.setAttributeNS(null, 'fill', 'black');

  //////////////
  //  Events  //
  //////////////
  var start = document.createElementNS(NS, 'symbol')
  defs.appendChild(start);
  start.id = 'start';
  var circ = document.createElementNS(NS, 'circle')
  start.appendChild(circ);
  circ.setAttributeNS(null, 'cx', 20);
  circ.setAttributeNS(null, 'cy', 20);
  circ.setAttributeNS(null, 'r', 20);
  circ.setAttributeNS(null, 'fill', 'transparent');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 2);
  start.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  var inter = document.createElementNS(NS, 'symbol')
  defs.appendChild(inter);
  inter.id = 'inter';
  var circ = document.createElementNS(NS, 'circle')
  inter.appendChild(circ);
  circ.setAttributeNS(null, 'cx', 20);
  circ.setAttributeNS(null, 'cy', 20);
  circ.setAttributeNS(null, 'r', 20);
  circ.setAttributeNS(null, 'fill', 'transparent');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 1);
  var circ = document.createElementNS(NS, 'circle')
  inter.appendChild(circ);
  circ.setAttributeNS(null, 'cx', 20);
  circ.setAttributeNS(null, 'cy', 20);
  circ.setAttributeNS(null, 'r', 17);
  circ.setAttributeNS(null, 'fill', 'transparent');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 1);
  inter.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  var boundary = document.createElementNS(NS, 'symbol')
  defs.appendChild(boundary);
  boundary.id = 'boundary';
  var circ = document.createElementNS(NS, 'circle')
  boundary.appendChild(circ);
  circ.setAttributeNS(null, 'cx', 20);
  circ.setAttributeNS(null, 'cy', 20);
  circ.setAttributeNS(null, 'r', 20);
  circ.setAttributeNS(null, 'fill', 'transparent');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 1);
  circ.setAttributeNS(null, 'stroke-dasharray', '4 4');
  var circ = document.createElementNS(NS, 'circle')
  boundary.appendChild(circ);
  circ.setAttributeNS(null, 'cx', 20);
  circ.setAttributeNS(null, 'cy', 20);
  circ.setAttributeNS(null, 'r', 17);
  circ.setAttributeNS(null, 'fill', 'transparent');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 1);
  circ.setAttributeNS(null, 'stroke-dasharray', '4 4');
  boundary.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  var end = document.createElementNS(NS, 'symbol')
  defs.appendChild(end);
  end.id = 'end';
  var circ = document.createElementNS(NS, 'circle')
  end.appendChild(circ);
  circ.setAttributeNS(null, 'cx', 20);
  circ.setAttributeNS(null, 'cy', 20);
  circ.setAttributeNS(null, 'r', 19);
  circ.setAttributeNS(null, 'fill', 'transparent');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 4);
  end.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  catch_msg = document.createElementNS(NS, 'symbol')
  defs.appendChild(catch_msg);
  catch_msg.id = 'catch_message';
  var path = document.createElementNS(NS, 'path')
  catch_msg.appendChild(path);
  path.setAttributeNS(null, 'd', 'M9,11 h22 v16 h-22 v-16 l11,9 l11,-9');
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 1);
  path.setAttributeNS(null, 'stroke-linejoin', 'round');
  path.setAttributeNS(null, 'fill', 'transparent');
  catch_msg.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  throw_msg = document.createElementNS(NS, 'symbol')
  defs.appendChild(throw_msg);
  throw_msg.id = 'throw_message';
  var path = document.createElementNS(NS, 'path')
  throw_msg.appendChild(path);
  path.setAttributeNS(null, 'd', 'M8,10 v18 h24 v-18 l-12,9 l-12,-9 M8,10 h24 l-12,8 l-12,-8');
  path.setAttributeNS(null, 'stroke', 'white');
  path.setAttributeNS(null, 'stroke-width', 2);
  path.setAttributeNS(null, 'stroke-linejoin', 'round');
  path.setAttributeNS(null, 'fill', 'black');
  throw_msg.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  timer_grp = document.createElementNS(NS, 'symbol')
  defs.appendChild(timer_grp);
  timer_grp.id = 'timer';
  var circle = document.createElementNS(NS, 'circle')
  timer_grp.appendChild(circle);
  var x=20, y=20, r=14, path_data='';
  circle.setAttributeNS(null, 'cx', x);
  circle.setAttributeNS(null, 'cy', y);
  circle.setAttributeNS(null, 'r', r);
  circle.setAttributeNS(null, 'stroke', 'black');
  circle.setAttributeNS(null, 'stroke-width', '1');
  circle.setAttributeNS(null, 'fill', 'transparent');
  var path = document.createElementNS(NS, 'path')
  timer_grp.appendChild(path);
  // draw marker for each 5 minutes
  for (var i=1; i<13; i++) {
    var deg = 180 - (i*30);
    var angle = deg * (Math.PI / 180);  // convert to radian
    path_data += ' M ' + (x + (r-1) * Math.sin(angle)) + ' ' + (y + (r-1) * Math.cos(angle));
    path_data += ' L ' + (x + (r-4) * Math.sin(angle)) + ' ' + (y + (r-4) * Math.cos(angle));
    };
  // draw hour hand and minute hand
  path_data += ' M ' + x + ' ' + y + ' L ' + (x+8) + ' ' + (y+1);
  path_data += ' M ' + x + ' ' + y + ' L ' + (x+3) + ' ' + (y-12);
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', '1');
  timer_grp.setAttributeNS(null, 'viewBox', '-2 -2 43 43');

  // var end_cancel = document.createElementNS(NS, 'symbol')
  // defs.appendChild(end_cancel);
  // end_cancel.id = 'end_cancel';
  // end_cancel.setAttributeNS(null, 'viewBox', '0 0 44 44');
  // var end_event = document.createElementNS(NS, 'use')
  // end_event.setAttributeNS(null, 'href', '#end_event')
  // end_cancel.appendChild(end_event)
  // var path = document.createElementNS(NS, 'path')
  // end_cancel.appendChild(path);
  // path.setAttributeNS(null, 'd', 'M12,12 L32,32 M12,32 L32,12');
  // path.setAttributeNS(null, 'stroke', 'black');
  // path.setAttributeNS(null, 'stroke-width', 4);

  ///////////////
  //  Gateway  //
  ///////////////
  var gateway = document.createElementNS(NS, 'path')
  defs.appendChild(gateway);
  gateway.id = 'gateway';
  var path_data = 'M 40 0 L 0 40 L 40 80 L 80 40 Z';
  gateway.setAttributeNS(null, 'd', path_data);
  gateway.setAttributeNS(null, 'stroke', 'black');
  gateway.setAttributeNS(null, 'stroke-width', 2);
  gateway.setAttributeNS(null, 'fill', 'transparent');

  // a none_gateway is an exclusive gateway with no marker visible
  var none_gateway = document.createElementNS(NS, 'symbol')
  defs.appendChild(none_gateway);
  none_gateway.id = 'none_gw';
  none_gateway.setAttributeNS(null, 'viewBox', '-1 -1 82 82');
  var gateway = document.createElementNS(NS, 'use')
  gateway.setAttributeNS(null, 'href', '#gateway')
  none_gateway.appendChild(gateway)

  // an excl_gateway is an exclusive gateway with the marker visible
  var excl_gateway = document.createElementNS(NS, 'symbol')
  defs.appendChild(excl_gateway);
  excl_gateway.id = 'exclusive_gw';
  excl_gateway.setAttributeNS(null, 'viewBox', '-1 -1 82 82');
  var gateway = document.createElementNS(NS, 'use')
  gateway.setAttributeNS(null, 'href', '#gateway')
  excl_gateway.appendChild(gateway)
  // <path d="M25,25 L29,25 L40,38
  // L51,25 L55,25 L42,40
  // L55,55 L50,55 L40,42
  // L29,55 L25,55 L38,40 Z" stroke="black" stroke-width="2"/> 
  var path = document.createElementNS(NS, 'path')
  excl_gateway.appendChild(path);
  var path_data = '';
  path_data += 'M25,25 L29,25 L40,38 ';
  path_data += 'L51,25 L55,25 L42,40 ';
  path_data += 'L55,55 L50,55 L40,42 ';
  path_data += 'L29,55 L25,55 L38,40 Z';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 4);
  path.setAttributeNS(null, 'fill', 'transparent');

  var incl_gateway = document.createElementNS(NS, 'symbol')
  defs.appendChild(incl_gateway);
  incl_gateway.id = 'inclusive_gw';
  incl_gateway.setAttributeNS(null, 'viewBox', '-1 -1 82 82');
  var gateway = document.createElementNS(NS, 'use')
  gateway.setAttributeNS(null, 'href', '#gateway')
  incl_gateway.appendChild(gateway)
  var circle = document.createElementNS(NS, 'circle')
  incl_gateway.appendChild(circle);
  var r = 40;
  var cx = r;
  var cy = r;
  circle.setAttributeNS(null, 'cx', cx);
  circle.setAttributeNS(null, 'cy', cy);
  circle.setAttributeNS(null, 'r', r / 2);
  circle.setAttributeNS(null, 'stroke', 'black');
  circle.setAttributeNS(null, 'stroke-width', 4);
  circle.setAttributeNS(null, 'fill', 'transparent');

  var par_gateway = document.createElementNS(NS, 'symbol')
  defs.appendChild(par_gateway);
  par_gateway.id = 'parallel_gw';
  par_gateway.setAttributeNS(null, 'viewBox', '-1 -1 82 82');
  var gateway = document.createElementNS(NS, 'use')
  gateway.setAttributeNS(null, 'href', '#gateway')
  par_gateway.appendChild(gateway)
  var path = document.createElementNS(NS, 'path')
  par_gateway.appendChild(path);
  var path_data = 'M 40,14 L 40,66 M 14,40 L 66,40 ';
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 8);
  path.setAttributeNS(null, 'fill', 'transparent');

  ////////////
  //  Task  //
  ////////////
  var task = document.createElementNS(NS, 'rect')
  defs.appendChild(task);
  task.id = 'task';
  task.setAttributeNS(null, 'width', 90);
  task.setAttributeNS(null, 'height', 70);
  task.setAttributeNS(null, 'rx', 10);
  task.setAttributeNS(null, 'ry', 10);
  task.setAttributeNS(null, 'stroke', 'black');
  task.setAttributeNS(null, 'stroke-width', 2);
  task.setAttributeNS(null, 'fill', 'transparent');

  var none_task = document.createElementNS(NS, 'symbol')
  defs.appendChild(none_task);
  none_task.id = 'none_task';
  none_task.setAttributeNS(null, 'viewBox', '-1 -1 92 72');
  var task = document.createElementNS(NS, 'use')
  task.setAttributeNS(null, 'href', '#task')
  none_task.appendChild(task)

  var user_task = document.createElementNS(NS, 'symbol')
  defs.appendChild(user_task);
  user_task.id = 'user_task';
  user_task.setAttributeNS(null, 'viewBox', '-1 -1 92 72');
  var task = document.createElementNS(NS, 'use')
  task.setAttributeNS(null, 'href', '#task')
  user_task.appendChild(task)
  var path = document.createElementNS(NS, 'path')
  user_task.appendChild(path);
  var path_data = [
    'M12.5,7.5 A 1.5,2 0 0 1 12.5,17.5 A 1.5,2 0 0 1 12.5,7.5 ',
    'M8.5,16 L5,18.5 v6.5 h15 v-6.5 L16.5,16 ',
    'M9,25 v-3.5 M16,25 v-3.5 '
    ].join('');
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 1.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  path.setAttributeNS(null, 'transform', 'scale(0.75)');

  var script_task = document.createElementNS(NS, 'symbol')
  defs.appendChild(script_task);
  script_task.id = 'script_task';
  script_task.setAttributeNS(null, 'viewBox', '-1 -1 92 72');
  var task = document.createElementNS(NS, 'use')
  task.setAttributeNS(null, 'href', '#task')
  script_task.appendChild(task)
  var grp = document.createElementNS(NS, 'g')
  script_task.appendChild(grp);
  var path = document.createElementNS(NS, 'path')
  grp.appendChild(path);
  var path_data = [
    'M40,10 C 20,25 20,55 40,60 S 60,100 40,110 ',
    'M40,10 h 60 ',
    'M100,10 C 80,25 80,55 100,60 S 120,100 100,110 ',
    'M100,110 h -60 ',
    ].join('');
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 3.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  var line = document.createElementNS(NS, 'path')
  grp.appendChild(line);
  line.setAttributeNS(null, 'd', 'M35,24 h 40');
  line.setAttributeNS(null, 'stroke', 'black');
  line.setAttributeNS(null, 'stroke-width', 5);
  line.setAttributeNS(null, 'fill', 'transparent');
  var line = document.createElementNS(NS, 'path')
  grp.appendChild(line);
  line.setAttributeNS(null, 'd', 'M42,48 h 40');
  line.setAttributeNS(null, 'stroke', 'black');
  line.setAttributeNS(null, 'stroke-width', 5);
  line.setAttributeNS(null, 'fill', 'transparent');
  var line = document.createElementNS(NS, 'path')
  grp.appendChild(line);
  line.setAttributeNS(null, 'd', 'M58,72 h 40');
  line.setAttributeNS(null, 'stroke', 'black');
  line.setAttributeNS(null, 'stroke-width', 5);
  line.setAttributeNS(null, 'fill', 'transparent');
  var line = document.createElementNS(NS, 'path')
  grp.appendChild(line);
  line.setAttributeNS(null, 'd', 'M64,96 h 40');
  line.setAttributeNS(null, 'stroke', 'black');
  line.setAttributeNS(null, 'stroke-width', 5);
  line.setAttributeNS(null, 'fill', 'transparent');
  grp.setAttributeNS(null, 'transform', 'scale(0.125), translate(10,20)');
  
  var recv_task = document.createElementNS(NS, 'symbol')
  defs.appendChild(recv_task);
  recv_task.id = 'recv_task';
  recv_task.setAttributeNS(null, 'viewBox', '-1 -1 92 72');
  var task = document.createElementNS(NS, 'use')
  task.setAttributeNS(null, 'href', '#task')
  recv_task.appendChild(task)
  var path = document.createElementNS(NS, 'path')
  recv_task.appendChild(path);
  // var path_data = 'M0,0 h26 v20 h-26 v-20 l13,10 l13,-10'
  var path_data = 'M1,1 h25 v17 h-25 v-17 l13,9 l13,-9'
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', 1.5);
  path.setAttributeNS(null, 'fill', 'transparent');
  path.setAttributeNS(null, 'transform', 'scale(0.6), translate(10,8)');

  var send_task = document.createElementNS(NS, 'symbol')
  defs.appendChild(send_task);
  send_task.id = 'send_task';
  send_task.setAttributeNS(null, 'viewBox', '-1 -1 92 72');
  var task = document.createElementNS(NS, 'use')
  task.setAttributeNS(null, 'href', '#task')
  send_task.appendChild(task)
  var grp = document.createElementNS(NS, 'g')
  send_task.appendChild(grp);
  var path = document.createElementNS(NS, 'path')
  grp.appendChild(path);
  var path_data = 'M0,0 v20 h26 v-20 l-13,10 l-13,-10'
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'stroke', 'white');
  path.setAttributeNS(null, 'stroke-width', 2);
  path.setAttributeNS(null, 'fill', 'black');
  var path = document.createElementNS(NS, 'path')
  grp.appendChild(path);
  path.setAttributeNS(null, 'd', 'M0,0 h26 l-13,10 l-13,-10');
  path.setAttributeNS(null, 'stroke', 'white');
  path.setAttributeNS(null, 'stroke-width', 2);
  path.setAttributeNS(null, 'fill', 'black');
  grp.setAttributeNS(null, 'transform', 'scale(0.6), translate(10,8)');
  
  var service_defn = document.createElementNS(NS, 'g');
  defs.appendChild(service_defn);
  service_defn.id = 'service_defn';
  var path = document.createElementNS(NS, 'path')
  service_defn.appendChild(path);
  var x=0, y=0, r=5, path_data='';
  var points = [];
  for (var i=1; i<64; i++) {
    var deg = 180 - (i*5.625);
    var angle = deg * (Math.PI / 180);  // convert to radian
    var start_x = Math.round((x + (r+4) * Math.sin(angle)));
    var start_y = Math.round((y + (r+4) * Math.cos(angle)));
    var end_x = Math.round((x + (r+10) * Math.sin(angle)));
    var end_y = Math.round((y + (r+10) * Math.cos(angle)));
    points.push([start_x, start_y, end_x, end_y]);
    };
  
  path_data += ' M ' + points[5][0] + ',' + points[5][1];
  path_data += ' L ' + (points[5][0]+4) + ',' + (points[5][1]-4);
  path_data += ' L ' + (points[9][0]+4) + ',' + (points[9][1]-4);
  path_data += ' L ' + points[9][0] + ',' + points[9][1];
  
  path_data += ' L ' + points[13][0] + ',' + points[13][1];
  path_data += ' L ' + (points[13][0]+6) + ',' + (points[13][1]);
  path_data += ' L ' + (points[16][0]+6) + ',' + (points[16][1]);
  path_data += ' L ' + points[16][0] + ',' + points[16][1];
  
  path_data += ' L ' + points[21][0] + ',' + points[21][1];
  path_data += ' L ' + (points[21][0]+4) + ',' + (points[21][1]+4);
  path_data += ' L ' + (points[25][0]+4) + ',' + (points[25][1]+4);
  path_data += ' L ' + points[25][0] + ',' + points[25][1];
  
  path_data += ' L ' + points[29][0] + ',' + points[29][1];
  path_data += ' L ' + (points[29][0]) + ',' + (points[29][1]+6);
  path_data += ' L ' + (points[32][0]) + ',' + (points[32][1]+6);
  path_data += ' L ' + points[32][0] + ',' + points[32][1];
  
  path_data += ' L ' + points[37][0] + ',' + points[37][1];
  path_data += ' L ' + (points[37][0]-4) + ',' + (points[37][1]+4);
  path_data += ' L ' + (points[41][0]-4) + ',' + (points[41][1]+4);
  path_data += ' L ' + points[41][0] + ',' + points[41][1];
  
  path_data += ' L ' + points[45][0] + ',' + points[45][1];
  path_data += ' L ' + (points[45][0]-6) + ',' + (points[45][1]);
  path_data += ' L ' + (points[48][0]-6) + ',' + (points[48][1]);
  path_data += ' L ' + points[48][0] + ',' + points[48][1];
  
  path_data += ' L ' + points[53][0] + ',' + points[53][1];
  path_data += ' L ' + (points[53][0]-4) + ',' + (points[53][1]-4);
  path_data += ' L ' + (points[57][0]-4) + ',' + (points[57][1]-4);
  path_data += ' L ' + points[57][0] + ',' + points[57][1];
  
  path_data += ' L ' + points[61][0] + ',' + points[61][1];
  path_data += ' L ' + (points[61][0]) + ',' + (points[61][1]-6);
  path_data += ' L ' + (points[0][0]) + ',' + (points[0][1]-6);
  path_data += ' L ' + points[0][0] + ',' + points[0][1];
  
  path_data += ' Z';
  
  path.setAttributeNS(null, 'd', path_data);
  path.setAttributeNS(null, 'fill', 'white');
  path.setAttributeNS(null, 'stroke', 'black');
  path.setAttributeNS(null, 'stroke-width', '1');
  
  var circ = document.createElementNS(NS, 'circle');
  service_defn.appendChild(circ);
  circ.setAttributeNS(null, 'cx', x);
  circ.setAttributeNS(null, 'cy', y);
  circ.setAttributeNS(null, 'r', r);
  circ.setAttributeNS(null, 'fill', 'white');
  circ.setAttributeNS(null, 'stroke', 'black');
  circ.setAttributeNS(null, 'stroke-width', 1);
  
  var service_task = document.createElementNS(NS, 'symbol');
  defs.appendChild(service_task);
  service_task.id = 'service_task';
  service_task.setAttributeNS(null, 'viewBox', '-1 -1 92 72');
  var task = document.createElementNS(NS, 'use')
  task.setAttributeNS(null, 'href', '#task')
  service_task.appendChild(task)
  var grp = document.createElementNS(NS, 'g')
  service_task.appendChild(grp);
  var serv_1 = document.createElementNS(NS, 'use');
  grp.appendChild(serv_1);
  serv_1.setAttributeNS(null, 'href', '#service_defn');
  serv_1.setAttributeNS(null, 'x', 0);
  serv_1.setAttributeNS(null, 'y', 0);
  var serv_2 = document.createElementNS(NS, 'use');
  grp.appendChild(serv_2);
  serv_2.setAttributeNS(null, 'href', '#service_defn');
  serv_2.setAttributeNS(null, 'x', 7);
  serv_2.setAttributeNS(null, 'y', 7);
  grp.setAttributeNS(null, 'transform', 'scale(0.4), translate(25,25)');

  var anchor = document.createElementNS(NS, 'rect');
  defs.appendChild(anchor);
  anchor.id = 'anchor';
  anchor.setAttributeNS(null, 'width', 8);
  anchor.setAttributeNS(null, 'height', 8);
  anchor.setAttributeNS(null, 'stroke', 'red');
  anchor.setAttributeNS(null, 'stroke-width', 0.5);
  anchor.setAttributeNS(null, 'fill', 'transparent');

  };

