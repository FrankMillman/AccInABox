<script type="text/javascript">
  function on_load() {
    var canvas = new_canvas(993, 545, document.body);
    canvas.style.background = 'paleturquoise';
    canvas.style.border = '1px solid darkblue';
    canvas.elements = [];
    ctx = canvas.getContext('2d');

    window_id = Math.random();
    send_request('get_diag', 'get_diag', null);
    }

  function send_request(url, event_id, args) {
    var xmlhttp=new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState==4 && xmlhttp.status==200) {
        process_response(xmlhttp.responseText);
        };
      };

    document.body.style.cursor = 'wait';
    args = JSON.stringify(args);
    var rnd = Math.random();
    var msg = url + '?e=' + event_id + '&a=' + args + '&wid=' + window_id + '&t=' + rnd;
    xmlhttp.open('GET', msg, true);
    xmlhttp.send(null);
    };

  function process_response(response_text) {
    document.body.style.cursor = 'default';
    if (!response_text.length) {return};
    //debug(response_text);
    try {
      var response = JSON.parse(response_text);
      for (var i=0;i<response.length;i++) {
        var element = response[i];
        var elem_type = element[0];
        //element[0] = ctx;
        switch(elem_type) {
        case 'pool': pool(element); break;
        case 'lane': lane(element); break;
        case 'start_event': start_event(element); break;
        case 'inter_event': inter_event(element); break;
        case 'end_event': end_event(element); break;
        case 'task': activity(element); break;
        case 'gateway': gateway(element); break;
        case 'sub_process': sub_process(element); break;
        case 'call_activity': call_activity(element); break;
        case 'sequence_flow': sequence_flow(element); break;
        case 'message_flow': message_flow(element); break;
        case 'association': association(element); break;
        case 'text_annotation': text_annotation(element); break;
        default: debug('unknown type ' + elem_type);
        };
      };
    }
    catch(err) {
      debug(err.description + ' ' + response_text);
      };
    };

  // this function exists in main.js - probably not needed here
  function new_canvas(width, height, parent) {
    var canvas = document.createElement('canvas');
    parent.appendChild(canvas);
    if (typeof(G_vmlCanvasManager) != 'undefined')
      G_vmlCanvasManager.initElement(canvas);  // IE only
    canvas.width = width;
    canvas.height = height;
    canvas.onclick = function(e) {
      if (!e) e=window.event;
      if (e.pageX || e.pageY) {
        var x = e.pageX;
        var y = e.pageY;
        }
      else {
        var x = e.clientX + document.body.scrollLeft +
          document.documentElement.scrollLeft;
        var y = e.clientY + document.body.scrollTop +
          document.documentElement.scrollTop;
        }

      var totalOffsetX = 0;
      var totalOffsetY = 0;

      var currentElement = canvas;
      do{
        totalOffsetX += currentElement.offsetLeft;
        totalOffsetY += currentElement.offsetTop;
        }
      while(currentElement = currentElement.offsetParent);

      x -= totalOffsetX;
      y -= totalOffsetY;

      for (var i=this.elements.length-1;i>=0;i--) {
        elem_coords = this.elements[i];
        if (x > elem_coords[1])
          if (x < (elem_coords[1] + elem_coords[3]))
            if (y > elem_coords[2])
              if (y < (elem_coords[2] + elem_coords[4])) {
                debug(elem_coords[0] + ' clicked');
                break;
                }
        }
      }
    return canvas;
    }

  function pool(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.strokeRect(x-0.5, y-0.5, w, h);

    if (text) {
      ctx.save();
      ctx.translate(x+15, y+(h/2));
      ctx.rotate(Math.PI * 1.5);
      ctx.textAlign = "center";
      ctx.fillText(text, 0, 0);
      ctx.restore();
      }
    }

  function lane(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.strokeRect(x-0.5, y-0.5, w, h);

    if (text) {
      ctx.save();
      ctx.translate(x+15, y+(h/2));
      ctx.rotate(Math.PI * 1.5);
      ctx.textAlign = "center";
      ctx.fillText(text, 0, 0);
      ctx.restore();
      }
    }

  function start_event(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6], event_type = args[7];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    if (w == h) {
      var r = w/2;
      var cx = x + r;  // centre x-coord
      var cy = y + r;  // centre y-coord
      }

    ctx.beginPath();
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.arc(cx,cy,r-1,0,Math.PI*2,true); // Outer circle
    ctx.fill();
    ctx.stroke();

    switch (event_type) {
      case 'none': break;
      case 'message': draw_message(cx, cy, r, false); break;
      case 'timer': draw_timer(cx, cy, r, false); break;
      case 'condition': draw_condition(cx, cy, r, false); break;
      case 'escalation': draw_escalation(cx, cy, r, false); break;
      case 'error': draw_error(cx, cy, r, false); break;
      }

    if (text) {
      ctx.fillStyle = "black";
      var text_w = ctx.measureText(text).width;
      var text_x = cx - (text_w / 2);
      var text_y = y + h + 15;
      ctx.fillText(text, text_x, text_y);
      }
    }

  function inter_event(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6], event_type = args[7],
    dashed = args[8], throwing = args[9];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    if (w == h) {
      var r = w/2;
      var cx = x + r;  // centre x-coord
      var cy = y + r;  // centre y-coord
      }

    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    if (dashed == true) {
      ctx.beginPath();
      ctx.strokeStyle = "white";
      ctx.arc(cx,cy,r,0,Math.PI*2,true);
      ctx.fill();
      ctx.beginPath();
      ctx.strokeStyle = "black";

      var n = r, alpha = Math.PI * 2 / n, i = -1;
      while( i < n ) {  // Outer circle
        var theta = alpha * i,
        theta2 = alpha * (i+1);
        ctx.moveTo(
          (Math.cos(theta) * r) + cx,
          (Math.sin(theta) * r) + cy);
        ctx.lineTo(
          (Math.cos(theta2) * r) + cx,
          (Math.sin(theta2) * r) + cy);
        ctx.stroke();
        i+=2;
        }

      var r = r*.8, n = r, alpha = Math.PI * 2 / n, i = -1;
      while( i < n ) {  // Inner circle
        var theta = alpha * i,
        theta2 = alpha * (i+1);
        ctx.moveTo(
          (Math.cos(theta) * r) + cx,
          (Math.sin(theta) * r) + cy);
        ctx.lineTo(
          (Math.cos(theta2) * r) + cx,
          (Math.sin(theta2) * r) + cy);
        ctx.stroke();
        i+=2;
        }
      ctx.closePath();
      }

    else {
      ctx.beginPath();
      ctx.arc(cx,cy,r,0,Math.PI*2,true); // Outer circle
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(cx,cy,r*.8,0,Math.PI*2,true); // Inner circle
      }
    ctx.stroke();

    switch (event_type) {
      case 'none': break;
      case 'message': draw_message(cx, cy, r, throwing); break;
      case 'timer': draw_timer(cx, cy, r, throwing); break;
      case 'condition': draw_condition(cx, cy, r, throwing); break;
      case 'escalation': draw_escalation(cx, cy, r, throwing); break;
      case 'error': draw_error(cx, cy, r, throwing); break;
      }

    if (text) {
      ctx.fillStyle = "black";
      var text_w = ctx.measureText(text).width;
      var text_x = cx - (text_w / 2);
      var text_y = y + h + 15;
      ctx.fillText(text, text_x, text_y);
      }
    }

  function end_event(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6], event_type = args[7];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    if (w == h) {
      var r = w/2;
      var cx = x + r;
      var cy = y + r;
      }

    ctx.beginPath();
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = r/5;
    ctx.arc(cx,cy,r*.9,0,Math.PI*2,true); // Outer circle
    ctx.fill();
    ctx.stroke();

    switch (event_type) {
      case 'none': break;
      case 'message': draw_message(cx, cy, r, true);
      case 'escalation': draw_escalation(cx, cy, r, true); break;
      case 'error': draw_error(cx, cy, r, true); break;
      }

    if (text) {
      ctx.fillStyle = "black";
      var text_w = ctx.measureText(text).width;
      var text_x = cx - (text_w / 2);
      var text_y = y + h + 15;
      ctx.fillText(text, text_x, text_y);
      }
    }

  function activity(args, lineWidth) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    if (lineWidth != undefined)
      ctx.lineWidth = lineWidth;
    else
      ctx.lineWidth = 1;
    roundedRect(x, y, w, h, 5);
    ctx.fillStyle = "black";

    var text_w = ctx.measureText(text).width;
    if (text_w > (w-20)) {
      var mid = text.length/2;
      var split = 0;
      for (var i=0;i<=mid;i++) {
        if (text.charAt(mid-i) == ' ')
          var split = mid-i;
        else if (text.charAt(mid+i) == ' ')
          var split = mid+i;
        if (split > 0) {
          var text_1 = text.substring(0, split);
          var text_2 = text.substring(split+1, text.length);
          break;
          }
        }
      if (split == 0) {
        var text_1 = text.substring(0, text.length/2);
        var text_2 = text.substring(text.length/2, text.length);
        }

      var text_w1 = ctx.measureText(text_1).width;
      var text_x1 = x + (w / 2) - (text_w1 / 2);
      var text_y1 = y + (h / 2 - 6);
      ctx.fillText(text_1, text_x1, text_y1);

      var text_w2 = ctx.measureText(text_2).width;
      var text_x2 = x + (w / 2) - (text_w2 / 2);
      var text_y2 = y + (h / 2 + 6);
      ctx.fillText(text_2, text_x2, text_y2);

      }
    else {
      var text_x = x + (w / 2) - (text_w / 2);
      var text_y = y + (h / 2);
      ctx.fillText(text, text_x, text_y);
      }
    }

  function call_activity(args) {
    lineWidth = 2.5;
    activity(args, lineWidth);
    draw_expander(args);
    }

  function sub_process(args) {
    lineWidth = 1;
    activity(args, lineWidth);
    draw_expander(args);
    }

  function gateway(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6], gw_type = args[7];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);
    if (w == h) {
      var r = w;
      }

    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.fillStyle = "white";
    ctx.lineWidth = 1;
    ctx.moveTo(x+(r/2), y);
    ctx.lineTo(x, y+(r/2));
    ctx.lineTo(x + (r/2), y+r);
    ctx.lineTo(x+r, y+(r/2));
    ctx.lineTo(x+(r/2), y);
    ctx.fill();
    ctx.stroke();

    if (text) {
      ctx.fillStyle = "black";
      var text_w = ctx.measureText(text).width;
      var text_x = x + (r/2) - (text_w / 2);
      var text_y = y - 10;
      ctx.fillText(text, text_x, text_y);
      }

    switch (gw_type) {
      case '': break;
      case 'exclusive':  draw_exclusive(x, y, r); break;
      case 'inclusive':  draw_inclusive(x, y, r); break;
      case 'parallel':  draw_parallel(x, y, r); break;
      }
    }

  function draw_exclusive(x, y, r) {
    ctx.beginPath();
    ctx.lineWidth = 4;
    ctx.moveTo(x+(r*2/3), y+(r/3));
    ctx.lineTo(x+(r/3), y+(r*2/3));
    ctx.moveTo(x+(r/3), y+(r/3));
    ctx.lineTo(x+(r*2/3), y+(r*2/3));
    ctx.stroke();
    }

  function draw_inclusive(x, y, r) {
    ctx.beginPath();
    ctx.lineWidth = 4;
    ctx.arc(x+(r/2),y+(r/2),r/4,0,Math.PI*2,true);
    ctx.stroke();
    }

  function draw_parallel(x, y, r) {
    ctx.beginPath();
    ctx.lineWidth = 4;
    ctx.moveTo(x+(r/2), y+ (r/5));
    ctx.lineTo(x+(r/2), y+(r*4/5));
    ctx.moveTo(x+(r/5), y+(r/2));
    ctx.lineTo(x+(r*4/5), y+(r/2));
    ctx.stroke();
    }

  function roundedRect(x, y, width, height, radius){
    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.fillStyle = "white";
    ctx.moveTo(x,y+radius);
    ctx.lineTo(x,y+height-radius);
    ctx.quadraticCurveTo(x,y+height,x+radius,y+height);
    ctx.lineTo(x+width-radius,y+height);
    ctx.quadraticCurveTo(x+width,y+height,x+width,y+height-radius);
    ctx.lineTo(x+width,y+radius);
    ctx.quadraticCurveTo(x+width,y,x+width-radius,y);
    ctx.lineTo(x+radius,y);
    ctx.quadraticCurveTo(x,y,x,y+radius);
    ctx.fill();
    ctx.stroke();
    }

  function draw_message(x, y, r, throwing) {
    var r = r * 0.6;

    var deg = 180 - (6 * 9);  // 126
    var angle = (Math.PI/180)*deg;
    var x1 = Math.round(x + r * Math.sin(angle));
    var y1 = Math.round(y + r * Math.cos(angle));

    var deg = 180 - (6 * 21);  // 54
    var angle = (Math.PI/180)*deg;
    var x2 = Math.round(x + r * Math.sin(angle));
    var y2 = Math.round(y + r * Math.cos(angle));

    var deg = 180 - (6 * 51);  // -126
    var angle = (Math.PI/180)*deg;
    var x4 = Math.round(x + r * Math.sin(angle));
    var y4 = Math.round(y + r * Math.cos(angle));

    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.strokeRect(x4, y4, x2-x4+1, y2-y4+1);
    ctx.moveTo(x4, y4);
    ctx.lineTo(x, y);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    }

  function draw_timer(x, y, r, throwing) {
    var r = r*.6;
    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.arc(x,y,r,0,Math.PI*2,true); // Inner circle
    for (var i=0;i<12;i++) {
      var deg = 180 - 30 * (i + 1)
      var angle = (Math.PI/180)*deg;
      var x1 = Math.round(x + (r*.9) * Math.sin(angle));
      var y1 = Math.round(y + (r*.9) * Math.cos(angle));
      var x2 = Math.round(x + (r*.7) * Math.sin(angle));
      var y2 = Math.round(y + (r*.7) * Math.cos(angle));
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      }

    var deg = 180 - 24
    var angle = (Math.PI/180)*deg;
    var x1 = Math.round(x + (r*.9) * Math.sin(angle));
    var y1 = Math.round(y + (r*.9) * Math.cos(angle));

    var deg = 180 - 96
    var angle = (Math.PI/180)*deg;
    var x2 = Math.round(x + (r*.6) * Math.sin(angle));
    var y2 = Math.round(y + (r*.6) * Math.cos(angle));

    ctx.moveTo(x1, y1);
    ctx.lineTo(x, y);
    ctx.lineTo(x2, y2);

    ctx.stroke();
    }

  function draw_condition(x, y, r, throwing) {
    var r = r * 0.6;

    var deg = 180 - (6 * 6);  // 144
    var angle = (Math.PI/180)*deg;
    var x1 = Math.round(x + r * Math.sin(angle));
    var y1 = Math.round(y + r * Math.cos(angle));

    var deg = 180 - (6 * 24);  // 60
    var angle = (Math.PI/180)*deg;
    var x2 = Math.round(x + r * Math.sin(angle));
    var y2 = Math.round(y + r * Math.cos(angle));

    var deg = 180 - (6 * 54);  // -114
    var angle = (Math.PI/180)*deg;
    var x4 = Math.round(x + r * Math.sin(angle));
    var y4 = Math.round(y + r * Math.cos(angle));

    ctx.beginPath();
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1;
    ctx.strokeRect(x4, y4, x2-x4, y2-y4);

    var h = y2 - y1 - 4;

    ctx.moveTo(x4+1, y4+2);
    ctx.lineTo(x1, y4+2);
    ctx.moveTo(x4+1, y4+5);
    ctx.lineTo(x1, y4+5);
    ctx.moveTo(x4+1, y4+9);
    ctx.lineTo(x1, y4+9);
    ctx.moveTo(x4+1, y2-2);
    ctx.lineTo(x1, y2-2);
    ctx.stroke();
    }

  function draw_escalation(x, y, r, throwing) {
    var r = r*.6;
    ctx.beginPath();
    ctx.lineWidth = 1;

    var deg = 180 - (6 * 0);  // 180
    var angle = (Math.PI/180)*deg;
    var x1 = Math.round(x + r * Math.sin(angle));
    var y1 = Math.round(y + r * Math.cos(angle));

    var deg = 180 - (6 * 22);  // 48
    var angle = (Math.PI/180)*deg;
    var x2 = Math.round(x + r * Math.sin(angle));
    var y2 = Math.round(y + r * Math.cos(angle));

    var deg = 180 - (6 * 38);  // -48
    var angle = (Math.PI/180)*deg;
    var x3 = Math.round(x + r * Math.sin(angle));
    var y3 = Math.round(y + r * Math.cos(angle));

    if (throwing) {
      ctx.strokeStyle = "white";
      ctx.fillStyle = "black";
      }
    else {
      ctx.strokeStyle = "black";
      ctx.fillStyle = "white";
      }

    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.lineTo(x, y);
    ctx.lineTo(x3, y3);
    ctx.lineTo(x1, y1);
    if (throwing)
      ctx.fill();
    else
      ctx.stroke();
    }

  function draw_error(x, y, r, throwing) {
    ctx.beginPath();
    ctx.lineWidth = 1;

    var r1 = r*.7;
    var deg = 180 - (6 * 8);  // 138
    var angle = (Math.PI/180)*deg;
    var x1 = Math.round(x + r1 * Math.sin(angle));
    var y1 = Math.round(y + r1 * Math.cos(angle));

    var deg = 180 - (6 * 38);  // -42
    var angle = (Math.PI/180)*deg;
    var x2 = Math.round(x + r1 * Math.sin(angle));
    var y2 = Math.round(y + r1 * Math.cos(angle));

    var r2 = r*.5;
    var deg = 180 - (6 * 23);  // 48
    var angle = (Math.PI/180)*deg;
    var x3 = Math.round(x + r2 * Math.sin(angle));
    var y3 = Math.round(y + r2 * Math.cos(angle));

    var deg = 180 - (6 * 53);  // -132
    var angle = (Math.PI/180)*deg;
    var x4 = Math.round(x + r2 * Math.sin(angle));
    var y4 = Math.round(y + r2 * Math.cos(angle));

    var r3 = r*.2;
    var deg = 180 - (6 * 13);  // 90
    var angle = (Math.PI/180)*deg;
    var x5 = Math.round(x + r3 * Math.sin(angle));
    var y5 = Math.round(y + r3 * Math.cos(angle));

    var deg = 180 - (6 * 47);  // -90
    var angle = (Math.PI/180)*deg;
    var x6 = Math.round(x + r3 * Math.sin(angle));
    var y6 = Math.round(y + r3 * Math.cos(angle));

    if (throwing) {
      ctx.strokeStyle = "white";
      ctx.fillStyle = "black";
      }
    else {
      ctx.strokeStyle = "black";
      ctx.fillStyle = "white";
      }

    ctx.moveTo(x1, y1);
    ctx.lineTo(x3, y3);
    ctx.lineTo(x6, y6);
    ctx.lineTo(x2, y2);
    ctx.lineTo(x4, y4);
    ctx.lineTo(x5, y5);
    ctx.lineTo(x1, y1);
    if (throwing)
      ctx.fill();
    else
      ctx.stroke();
    }

  function draw_expander(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6];
    ctx.beginPath();
    ctx.lineWidth = 1;
    var x1 = x+(w/2)-7, y1 = y+h-16
    ctx.strokeRect(x1, y1, 14, 14);
    ctx.lineWidth = 1.5;
    ctx.moveTo(x1+2, y1+7);
    ctx.lineTo(x1+12, y1+7);
    ctx.moveTo(x1+7, y1+2);
    ctx.lineTo(x1+7, y1+12);
    ctx.stroke();
    }

  function sequence_flow(args) {
    var elem_id = args[1], points = args[2];
    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.strokeStyle = "black";
    ctx.moveTo(points[0][0], points[0][1]);
    if (points.length == 2) {
      ctx.lineTo(points[1][0], points[1][1]);
      }
    else {
      for (var i=1;i<(points.length-1);i++) {
        if (points[i-1][0] == points[i][0]) {  // vertical
          if (points[i][0] == points[i+1][0]) {  // no change
            ctx.lineTo(points[i][0], points[i][1]);
            }
          else if (points[i-1][1] > points[i][1]) {  // upwards
            ctx.lineTo(points[i][0], points[i][1] + 5);
            if (points[i][0] < points[i+1][0]) {  // right
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] + 5, points[i][1]);
              }
            else {  // left
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] - 5, points[i][1]);
              }
            }
          else {  // downwards
            ctx.lineTo(points[i][0], points[i][1] - 5);
            if (points[i][0] < points[i+1][0]) {  // right
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] + 5, points[i][1]);
              }
            else {  // left
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] - 5, points[i][1]);
              }
            }
          }
        else {  // horizontal
          if (points[i][1] == points[i+1][1]) {  // no change
            ctx.lineTo(points[i][0], points[i][1]);
            }
          else if (points[i-1][0] > points[i][0]) {  // left
            ctx.lineTo(points[i][0] + 5, points[i][1]);
            if (points[i][1] < points[i+1][1]) {  // downwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] + 5);
              }
            else {  // upwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] - 5);
              }
            }
          else {  // right
            ctx.lineTo(points[i][0] - 5, points[i][1]);
            if (points[i][1] < points[i+1][1]) {  // downwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] + 5);
              }
            else {  // upwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] - 5);
              }
            }
          }
        }
      }
    var last_x = points[points.length-1][0];
    var last_y = points[points.length-1][1];
    ctx.lineTo(last_x, last_y);
    ctx.stroke();

    // draw arrowhead
    ctx.beginPath();
    ctx.moveTo(last_x, last_y);
    if (last_x == points[points.length-2][0]) {  // vertical
      if (last_y > points[points.length-2][1]) {  // downwards
        ctx.lineTo(last_x-3, last_y-10);
        ctx.lineTo(last_x+3, last_y-10);
        }
      else {  // upwards
        ctx.lineTo(last_x-3, last_y+10);
        ctx.lineTo(last_x+3, last_y+10);
        }
      }
    else {  // horizontal
      if (last_x > points[points.length-2][0]) {  // right
        ctx.lineTo(last_x-10, last_y-3);
        ctx.lineTo(last_x-10, last_y+3);
        }
      else {  // left
        ctx.lineTo(last_x+10, last_y-3);
        ctx.lineTo(last_x+10, last_y+3);
        }
      }
    ctx.fillStyle = "black";
    ctx.fill();
    }

  function message_flow(args) {
    var elem_id = args[1], points = args[2];


    var cnr = 2;

    var dashValues = [6, 4];
    var dashIdx = 0;
    var dashOffset = dashValues[0];

    function dashLineTo(x1, y1) {
      var length = Math.sqrt( (x1-dashX)*(x1-dashX) + (y1-dashY)*(y1-dashY) );
      var dx = (x1-dashX) / length;
      var dy = (y1-dashY) / length;

      var dist = 0;
      while (dist < length) {
        var dashLength = Math.min(dashValues[dashIdx], length-dist);
        dist += dashLength;

        if (dashIdx % 2 == 0)
          ctx.moveTo(dashX, dashY);

        dashX += dashLength * dx;
        dashY += dashLength * dy;

        if (dashIdx % 2 == 0)
          ctx.lineTo(dashX, dashY);

        dashOffset += dashLength;
        if (dashOffset > dashValues[dashIdx]) {
          dashOffset -= dashValues[dashIdx];
          dashIdx = (dashIdx+1) % dashValues.length;
          }
        }
      }

    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.strokeStyle = "black";

    //ctx.moveTo(points[0][0], points[0][1]);
    var dashX = points[0][0], dashY = points[0][1];
    if (points.length == 2) {
      //ctx.lineTo(points[1][0], points[1][1]);
      dashLineTo(points[1][0], points[1][1]);
      }
    else {
      for (var i=1;i<(points.length-1);i++) {
        if (points[i-1][0] == points[i][0]) {  // vertical
          if (points[i][0] == points[i+1][0]) {  // no change
            //ctx.lineTo(points[i][0], points[i][1]);
            dashLineTo(points[i][0], points[i][1]);
            }
          else if (points[i-1][1] > points[i][1]) {  // upwards
            //ctx.lineTo(points[i][0], points[i][1] + cnr);
            dashLineTo(points[i][0], points[i][1] + cnr);
            if (points[i][0] < points[i+1][0]) {  // right
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] + cnr, points[i][1]);
              }
            else {  // left
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] - cnr, points[i][1]);
              }
            }
          else {  // downwards
            //ctx.lineTo(points[i][0], points[i][1] - cnr);
            dashLineTo(points[i][0], points[i][1] - cnr);
            if (points[i][0] < points[i+1][0]) {  // right
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] + cnr, points[i][1]);
              }
            else {  // left
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] - cnr, points[i][1]);
              }
            }
          }
        else {  // horizontal
          if (points[i][1] == points[i+1][1]) {  // no change
            //ctx.lineTo(points[i][0], points[i][1]);
            dashLineTo(points[i][0], points[i][1]);
            }
          else if (points[i-1][0] > points[i][0]) {  // left
            //ctx.lineTo(points[i][0] + cnr, points[i][1]);
            dashLineTo(points[i][0] + cnr, points[i][1]);
            if (points[i][1] < points[i+1][1]) {  // downwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] + cnr);
              }
            else {  // upwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] - cnr);
              }
            }
          else {  // right
            //ctx.lineTo(points[i][0] - cnr, points[i][1]);
            dashLineTo(points[i][0] - cnr, points[i][1]);
            if (points[i][1] < points[i+1][1]) {  // downwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] + cnr);
              }
            else {  // upwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] - cnr);
              }
            }
          }
        }
      }
    var last_x = points[points.length-1][0];
    var last_y = points[points.length-1][1];
    //ctx.lineTo(last_x, last_y);
    dashLineTo(last_x, last_y);
    ctx.stroke();

    // draw arrowhead
    ctx.beginPath();
    ctx.moveTo(last_x, last_y);
    if (last_x == points[points.length-2][0]) {  // vertical
      if (last_y > points[points.length-2][1]) {  // downwards
        ctx.lineTo(last_x-3, last_y-10);
        ctx.lineTo(last_x+3, last_y-10);
        ctx.lineTo(last_x, last_y);
        }
      else {  // upwards
        ctx.lineTo(last_x-3, last_y+10);
        ctx.lineTo(last_x+3, last_y+10);
        ctx.lineTo(last_x, last_y);
        }
      }
    else {  // horizontal
      if (last_x > points[points.length-2][0]) {  // right
        ctx.lineTo(last_x-10, last_y-3);
        ctx.lineTo(last_x-10, last_y+3);
        ctx.lineTo(last_x, last_y);
        }
      else {  // left
        ctx.lineTo(last_x+10, last_y-3);
        ctx.lineTo(last_x+10, last_y+3);
        ctx.lineTo(last_x, last_y);
        }
      }
    //ctx.fillStyle = "black";
    ctx.stroke();
    }

  function association(args) {
    var elem_id = args[1], points = args[2];

    var cnr = 2;

    var dashValues = [2, 6];
    var dashIdx = 0;
    var dashOffset = dashValues[0];

    function dashLineTo(x1, y1) {
      var length = Math.sqrt( (x1-dashX)*(x1-dashX) + (y1-dashY)*(y1-dashY) );
      var dx = (x1-dashX) / length;
      var dy = (y1-dashY) / length;

      var dist = 0;
      while (dist < length) {
        var dashLength = Math.min(dashValues[dashIdx], length-dist);
        dist += dashLength;

        if (dashIdx % 2 == 0)
          ctx.moveTo(dashX, dashY);

        dashX += dashLength * dx;
        dashY += dashLength * dy;

        if (dashIdx % 2 == 0)
          ctx.lineTo(dashX, dashY);

        dashOffset += dashLength;
        if (dashOffset > dashValues[dashIdx]) {
          dashOffset -= dashValues[dashIdx];
          dashIdx = (dashIdx+1) % dashValues.length;
          }
        }
      }

    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.strokeStyle = "black";
    //ctx.moveTo(points[0][0], points[0][1]);
    var dashX = points[0][0], dashY = points[0][1];
    if (points.length == 2) {
      //ctx.lineTo(points[1][0], points[1][1]);
      dashLineTo(points[1][0], points[1][1]);
      }
    else {
      for (var i=1;i<(points.length-1);i++) {
        if (points[i-1][0] == points[i][0]) {  // vertical
          if (points[i][0] == points[i+1][0]) {  // no change
            //ctx.lineTo(points[i][0], points[i][1]);
            dashLineTo(points[i][0], points[i][1]);
            }
          else if (points[i-1][1] > points[i][1]) {  // upwards
            //ctx.lineTo(points[i][0], points[i][1] + cnr);
            dashLineTo(points[i][0], points[i][1] + cnr);
            if (points[i][0] < points[i+1][0]) {  // right
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] + cnr, points[i][1]);
              dashX = points[i][0] + cnr, dashY = points[i][1];
              }
            else {  // left
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] - cnr, points[i][1]);
              dashX = points[i][0] - cnr, dashY = points[i][1];
              }
            }
          else {  // downwards
            //ctx.lineTo(points[i][0], points[i][1] - cnr);
            dashLineTo(points[i][0], points[i][1] - cnr);
            if (points[i][0] < points[i+1][0]) {  // right
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] + cnr, points[i][1]);
              dashX = points[i][0] + cnr, dashY = points[i][1];
              }
            else {  // left
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0] - cnr, points[i][1]);
              dashX = points[i][0] - cnr, dashY = points[i][1];
              }
            }
          }
        else {  // horizontal
          if (points[i][1] == points[i+1][1]) {  // no change
            //ctx.lineTo(points[i][0], points[i][1]);
            dashLineTo(points[i][0], points[i][1]);
            }
          else if (points[i-1][0] > points[i][0]) {  // left
            //ctx.lineTo(points[i][0] + cnr, points[i][1]);
            dashLineTo(points[i][0] + cnr, points[i][1]);
            if (points[i][1] < points[i+1][1]) {  // downwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] + cnr);
              dashX = points[i][0], dashY = points[i][1] + cnr;
              }
            else {  // upwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] - cnr);
              dashX = points[i][0], dashY = points[i][1] - cnr;
              }
            }
          else {  // right
            //ctx.lineTo(points[i][0] - cnr, points[i][1]);
            dashLineTo(points[i][0] - cnr, points[i][1]);
            if (points[i][1] < points[i+1][1]) {  // downwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] + cnr);
              dashX = points[i][0], dashY = points[i][1] + cnr;
              }
            else {  // upwards
              ctx.quadraticCurveTo(points[i][0], points[i][1],
                points[i][0], points[i][1] - cnr);
              dashX = points[i][0], dashY = points[i][1] - cnr;
              }
            }
          }
        }
      }
    var last_x = points[points.length-1][0];
    var last_y = points[points.length-1][1];
    //ctx.lineTo(last_x, last_y);
    dashLineTo(last_x, last_y);
    ctx.stroke();
    }

  function text_annotation(args) {
    var elem_id = args[1], x = args[2], y = args[3],
    w = args[4], h = args[5], text = args[6];
    ctx.canvas.elements.push([elem_id, x, y, w, h]);

    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.strokeStyle = "black";
    ctx.moveTo(x+w-1, y);
    ctx.lineTo(x, y);
    ctx.lineTo(x, y+h-1);
    ctx.lineTo(x+w-1, y+h-1);
    ctx.stroke();
    ctx.fillText(text, x+5, y+15);
    }

  debug_setup = false;
  function setup_debug () {
    var debug_row = document.createElement('div');
    debug_row.id = 'debug';
    document.body.appendChild(debug_row);
    debug_setup = true;
    }

  str = new String();
  function debug(msg) {
    if (!debug_setup) setup_debug();
    if (str.length) str += '<br>';
    str += msg;
    //if (msg == '>')
    //  str += '<br>';
    //else
    //  str += '&nbsp;';
    document.getElementById('debug').innerHTML = str;
    }

</script>
