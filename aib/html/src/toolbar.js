create_frame_toolbar = function(toolbar, json_args) {
  //debug3(JSON.stringify(json_args));

  toolbar.style.border = '1px solid lightgrey';
  toolbar.style.height = '28px';
  var frame = toolbar.frame;
  var page = frame.page;
  var title = json_args[0], tool_list = json_args[1];
  if (title !== null) {
    var text = document.createElement('span');
    text.appendChild(document.createTextNode(title));
    text.style.fontWeight = 'bold';
    text.style.marginLeft = '5px';
    text.style.marginTop = '5px';
    text.style.marginRight = '10px';
    text.style[cssFloat] = 'left';
    toolbar.appendChild(text);
    };
  for (var i=0; i<tool_list.length; i++) {
    var tool = tool_list[i];
    switch(tool.type) {
      case 'btn': {
        var label = tool.label;
        var text = '';  // convert '&' to underline
        for (var j=0; j<label.length; j++) {
          if (label[j] === '&') {
            if (label[j+1] === '&')
              text += '&';
            else {
              // set up label[j+1] as hotkey!
              text += '<u>';
              text += label[j+1];
              text += '</u>';
              };
            j++;
            }
          else
            text += label[j];
          }
        var btn = document.createElement('div');
        btn.style[cssFloat] = 'left';

//        if (tool.ref != frame.obj_list.length)
//          debug3(tool.ref + ' != ' + frame.obj_list.length);
        //btn.pos = frame.obj_list.length;
        //frame.obj_list.push(btn);
        frame.form.obj_dict[tool.ref] = btn;
        btn.tabIndex = -1  // remove from tab order
        btn.ref = tool.ref;

        btn.style.border = '1px solid darkgrey';
        btn.style.marginLeft = '5px';
        btn.style.marginRight = '5px';
        btn.style.marginTop = '5px';
        btn.style.paddingLeft = '5px';
        btn.style.paddingRight = '5px';
        btn.style.background = 'lightgrey';
        btn.style.position = 'relative';
        btn.innerHTML = text;
        btn.title = tool.tip;
        btn.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
          //var args = [frame.root_id, frame.form_id, this.ref, grid.active_row];
          var args = [this.ref, grid.active_row];
          send_request('clicked', args);
          //DOMViewerObj = document.getElementById("toolbar")
          //DOMViewerName = null;
          //window.open('../tests/domviewer.html');
          frame.form.current_focus.focus();
          };

          if (tool.shortcut !== null) {
            var type_key = tool.shortcut.split(',');
            if (type_key[0] === 'normal')
              page.kbd_shortcuts['normal'][type_key[1]] = btn;
            else if (type_key[0] === 'alt')
              page.kbd_shortcuts['alt'][type_key[1]] = btn;
            else if (type_key[0] === 'ctrl')
              page.kbd_shortcuts['ctrl'][type_key[1]] = btn;
            else if (type_key[0] === 'shift')
              page.kbd_shortcuts['shift'][type_key[1]] = btn;
            };

        toolbar.appendChild(btn)
        break;
        }
      case 'img':
        //debug3('IMAGE'); break;
        var btn = document.createElement('div');
        btn.style[cssFloat] = 'left';
        btn.style.backgroundImage = 'url(images/' + tool.name + '.png)';
        btn.style.width = '16px';
        btn.style.height = '16px';
        btn.style.marginLeft = '5px';
        btn.style.marginRight = '2px';
        btn.style.marginTop = '5px';
        btn.style.position = 'relative';

        frame.form.obj_dict[tool.ref] = btn;
        btn.tabIndex = -1  // remove from tab order
        btn.ref = tool.ref;

        btn.title = tool.tip;
        btn.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
          //var args = [frame.root_id, frame.form_id, this.ref, grid.active_row];
          var args = [this.ref];
          if (frame.ctrl_grid !== null)
            args.push(frame.ctrl_grid.active_row);
          send_request('clicked', args);
          //DOMViewerObj = document.getElementById("toolbar")
          //DOMViewerName = null;
          //window.open('../tests/domviewer.html');
          frame.form.current_focus.focus();
          };

          if (tool.shortcut !== null) {
            var type_key = tool.shortcut.split(',');
            if (type_key[0] === 'normal')
              page.kbd_shortcuts['normal'][type_key[1]] = btn;
            else if (type_key[0] === 'alt')
              page.kbd_shortcuts['alt'][type_key[1]] = btn;
            else if (type_key[0] === 'ctrl')
              page.kbd_shortcuts['ctrl'][type_key[1]] = btn;
            else if (type_key[0] === 'shift')
              page.kbd_shortcuts['shift'][type_key[1]] = btn;
            };

        toolbar.appendChild(btn)
        break;
/*
      case 'ins_row': {
        var ctrl_grid = toolbar.frame.ctrl_grid;
        ctrl_grid.insert_ok = true;
        var btn = document.createElement('div');
        btn.style[cssFloat] = 'left';
        btn.style.backgroundImage = 'url(' + iInsert_src + ')';
        btn.style.width = '16px';
        btn.style.height = '16px';
        btn.style.marginLeft = '5px';
        btn.style.marginRight = '2px';
        btn.style.marginTop = '5px';
        btn.style.position = 'relative';

        btn.title = tool.tip;
        btn.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
          ctrl_grid.req_insert();
          frame.form.current_focus.focus();
          };
        toolbar.appendChild(btn)
        break;
        }
      case 'del_row': {
        var ctrl_grid = toolbar.frame.ctrl_grid;
        ctrl_grid.delete_ok = true;
        ctrl_grid.confirm_delete = tool.confirm;
        var btn = document.createElement('div');
        btn.style[cssFloat] = 'left';
        btn.style.backgroundImage = 'url(' + iDelete_src + ')';
        btn.style.width = '16px';
        btn.style.height = '16px';
        btn.style.marginLeft = '5px';
        btn.style.marginRight = '2px';
        btn.style.marginTop = '5px';
        btn.style.position = 'relative';

        btn.title = tool.tip;
        btn.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
          ctrl_grid.req_delete();
          frame.form.current_focus.focus();
          };
        toolbar.appendChild(btn)
        break;
        }
*/
      case 'nav': {

        var ctrl_grid = toolbar.frame.ctrl_grid;
        ctrl_grid.navigate_ok = true;

        // FIRST
        //var nav = document.createElement('div');
        //var nav = iFirst;
        var nav = document.createElement('div');
        nav.style.backgroundImage = 'url(' + iFirst_src + ')';
        nav.style[cssFloat] = 'left';
        //nav.style.border = '1px solid darkgrey';
        nav.style.width = '16px';
        nav.style.height = '16px';
        nav.style.marginLeft = '5px';
        nav.style.marginRight = '2px';
        nav.style.marginTop = '5px';
        //nav.style.background = 'lightgrey';
        nav.style.position = 'relative';
        nav.title = 'First';
        nav.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
          if (ctrl_grid.active_row === 0)
            return;
          var args = [frame.ref, 'first'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          };

        page.kbd_shortcuts['ctrl'][36] = nav;  // Ctrl+Home

        toolbar.appendChild(nav);

/*
        if (EX) nav.innerHTML = '^'; else {
          var canvas = new_canvas(15, 15, nav);
          var ctx = canvas.getContext('2d');
          ctx.beginPath();
          ctx.moveTo(4.5, 7.5);
          ctx.lineTo(12.5, 1.5);
          ctx.lineTo(12.5, 12.5);
          ctx.lineTo(4.5, 7.5);
          ctx.lineTo(4.5, 1.5);
          ctx.lineTo(2.5, 1.5);
          ctx.lineTo(2.5, 12.5);
          ctx.lineTo(4.5, 12.5);
          ctx.lineTo(4.5, 7.5);
          ctx.fillStyle = 'black';
          ctx.fill();
          };
*/

        // PREV
        //var nav = document.createElement('div');
        //var nav = iPrev;
        var nav = document.createElement('div');
        nav.style.backgroundImage = 'url(' + iPrev_src + ')';
        nav.style[cssFloat] = 'left';
        //nav.style.border = '1px solid darkgrey';
        nav.style.width = '16px';
        nav.style.height = '16px';
        nav.style.marginLeft = '2px';
        nav.style.marginRight = '2px';
        nav.style.marginTop = '5px';
        //nav.style.background = 'lightgrey';
        nav.style.position = 'relative';
        nav.title = 'Prev';
        nav.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
          if (ctrl_grid.active_row === 0)
            return;
          var args = [frame.ref, 'prev'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          }

        page.kbd_shortcuts['ctrl'][38] = nav;  // Ctrl+Up

        toolbar.appendChild(nav);

/*
        if (EX) nav.innerHTML = '&lt;'; else {
          var canvas = new_canvas(15, 15, nav);
          var ctx = canvas.getContext('2d');
          ctx.beginPath();
          ctx.moveTo(11.5, 1.5);
          ctx.lineTo(11.5, 12.5);
          ctx.lineTo(3.5, 7.5);
          ctx.fillStyle = 'black';
          ctx.fill();
          };
*/

        // ROW COUNTER
        row_count = document.createElement('div');
        row_count.style[cssFloat] = 'left';
        row_count.style.marginTop = '5px';
        row_count.style.position = 'relative';
        ctrl_grid.form_row_count = row_count;
        if (ctrl_grid.row_count !== null)
          row_count.innerHTML = ctrl_grid.row_count.innerHTML;  // initial value
        toolbar.appendChild(row_count);

        // NEXT
        //var nav = document.createElement('div');
        //var nav = iNext;
        var nav = document.createElement('div');
        nav.style.backgroundImage = 'url(' + iNext_src + ')';
        nav.style[cssFloat] = 'left';
        //nav.style.border = '1px solid darkgrey';
        nav.style.width = '16px';
        nav.style.height = '16px';
        nav.style.marginLeft = '2px';
        nav.style.marginRight = '2px';
        nav.style.marginTop = '5px';
        //nav.style.background = 'lightgrey';
        nav.style.position = 'relative';
        nav.title = 'Next';
        nav.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
//          if (ctrl_grid.active_row === (ctrl_grid.total_rows()-1))
          if (ctrl_grid.active_row === (ctrl_grid.num_data_rows))
            return;
          var args = [frame.ref, 'next'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          };

        page.kbd_shortcuts['ctrl'][40] = nav;  // Ctrl+Down

        toolbar.appendChild(nav);

/*
        if (EX) nav.innerHTML = '&gt;'; else {
          var canvas = new_canvas(15, 15, nav);
          var ctx = canvas.getContext('2d');
          ctx.beginPath();
          ctx.moveTo(3.5, 1.5);
          ctx.lineTo(3.5, 12.5);
          ctx.lineTo(11.5, 7.5);
          ctx.fillStyle = 'black';
          ctx.fill();
          };
*/

        // LAST
        //var nav = document.createElement('div');
        //var nav = iLast;
        var nav = document.createElement('div');
        nav.style.backgroundImage = 'url(' + iLast_src + ')';
        nav.style[cssFloat] = 'left';
        //nav.style.border = '1px solid darkgrey';
        nav.style.width = '16px';
        nav.style.height = '16px';
        nav.style.marginLeft = '2px';
        nav.style.marginRight = '5px';
        nav.style.marginTop = '5px';
        //nav.style.background = 'lightgrey';
        nav.style.position = 'relative';
        nav.title = 'Last';
        nav.onclick = function(e) {
          var frame = toolbar.frame;
          if (frame.disable_count) return false;
//          if (ctrl_grid.active_row === (ctrl_grid.total_rows()-1))
          if (ctrl_grid.active_row === (ctrl_grid.num_data_rows))
            return;
          var args = [frame.ref, 'last'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          };

        page.kbd_shortcuts['ctrl'][35] = nav;  // Ctrl+End

        toolbar.appendChild(nav);

/*
        if (EX) nav.innerHTML = 'v'; else {
          var canvas = new_canvas(15, 15, nav);
          var ctx = canvas.getContext('2d');
          ctx.beginPath();
          ctx.moveTo(10.5, 7.5);
          ctx.lineTo(2.5, 1.5);
          ctx.lineTo(2.5, 12.5);
          ctx.lineTo(10.5, 7.5);
          ctx.lineTo(10.5, 1.5);
          ctx.lineTo(12.5, 1.5);
          ctx.lineTo(12.5, 12.5);
          ctx.lineTo(10.5, 12.5);
          ctx.lineTo(10.5, 7.5);
          ctx.fillStyle = 'black';
          ctx.fill();
          };
*/

        break;
        }
      case 'text': {
        var text = document.createElement('div');
        text.style[cssFloat] = 'left';
        text.style.marginTop = '5px';
        text.style.width = tool.lng + 'px';
        text.style.position = 'relative';

        frame.form.obj_dict[tool.ref] = text;
        text.tabIndex = -1  // remove from tab order
        text.ref = tool.ref;

        text.set_value_from_server = function(value) {
          this.innerHTML = value.replace(/ /g, '\xa0');
          };

        toolbar.appendChild(text);

        break;
        }
      default: debug3(tool.type + ' UNKNOWN'); break;
      };
    };
  };
