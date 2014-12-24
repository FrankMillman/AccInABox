active_roots = {};  //new Object();
root_zindex = [];  //new Array();
current_form = null;
// next 2 must be global, because 'parent' can change between 'press' and 'release'
click_from_kbd = false;  // prevent keydown repeat
ignore_enter = false;  // allow 'enter' from textarea

function setup_form(args) {
  //debug(JSON.stringify(args));

  var save_pages = [];
  var save_frames = [];
  var save_blocks = [];
  var save_vbox = [];
  var subtype_name = null;

  for (var i=0, args_length=args.length; i<args_length; i++) {
    var elem = args[i];
    switch(elem[0]) {
      case 'root': {
        var root_id = elem[1].root_id;
        var root = [];  // can contain multiple forms
        active_roots[root_id] = root;
        root.zindex = root_zindex.length;
        root_zindex.push(root);
        break;
        };

      case 'form': {
        var form_id = elem[1].form_id;
        var root_id = form_id.split('_')[0];
        var root = active_roots[root_id];

        var form = document.createElement('div');
        form.className = 'form';
        //form.style.position = 'absolute';
        //form.style.border = '2px solid grey';
        //form.style.background = 'white';
        document.body.appendChild(form);
        form.internal = false;  // do send 'change_focus' events

        if (root.length)  // this is not the top-level form
          root[root.length-1].disable_controls();

        form.style.zIndex = (root.zindex*100) + root.length;

        root.push(form);

        form.root = root;
        form.root_id = root_id;
        form.form_id = form_id;

        form.disable_count = 0;
        form.obj_dict = {};
        form.css_classes = [];
        form.focus_from_server = false;
        form.current_focus = null;
        form.setting_focus = null;  // IE workaround

        var header = document.createElement('div');
        form.appendChild(header);
        header.form = form;
        form.header = header;
        header.className = 'form_header';
        //header.style.background = '#C3D9FF';
        //header.style.fontWeight = 'bold';
        //header.style.paddingLeft = '5px';
        //header.style.borderBottom = '1px solid grey';
        //header.style.cursor = 'default';

        header.appendChild(document.createTextNode(elem[1].title));
        // to prevent selection of text - IE only
        header.onselectstart = function(){return false};

        var ctrl_block = document.createElement('div');
        ctrl_block.style[cssFloat] = 'right';
        header.appendChild(ctrl_block);

        var minim = document.createElement('div');
        minim.style[cssFloat] = 'left';
        minim.style.width = '12px';
        minim.style.height = '12px';
        minim.style.margin = '1px 2px 1px 1px';
        //minim.style.background = 'lightgrey';
        minim.style.backgroundImage = 'url(' + iMinim_src + ')';
        minim.style.borderTop = '1px solid white';
        minim.style.borderLeft = '1px solid white';
        minim.style.borderRight = '1px solid black';
        minim.style.borderBottom = '1px solid black';
        minim.style.position = 'relative';
        minim.title = 'Minimise';
        minim.onclick = function(e) {
          // this.parentNode.parentNode.parentNode.req_close();
          };
        ctrl_block.appendChild(minim);

/*
        var canvas = new_canvas(12, 12, minim);
        var ctx = canvas.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(2.5, 9.5);
        ctx.lineTo(9.5, 9.5);
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = 'black';
        ctx.stroke();
*/

        var close = document.createElement('div');
        close.style[cssFloat] = 'left';
        close.style.width = '12px';
        close.style.height = '12px';
        close.style.margin = '1px 2px 1px 1px';
        //close.style.background = 'lightgrey';
        close.style.backgroundImage = 'url(' + iClose_src + ')';
        close.style.borderTop = '1px solid white';
        close.style.borderLeft = '1px solid white';
        close.style.borderRight = '1px solid black';
        close.style.borderBottom = '1px solid black';
        close.style.position = 'relative';
        close.title = 'Close (Shift+F4)';
        close.onclick = function(e) {
          var form = this.parentNode.parentNode.parentNode;
          if (form.disable_count)
            return false;
          form.req_close();
          };
        ctrl_block.appendChild(close);

/*
        var canvas = new_canvas(12, 12, close);
        var ctx = canvas.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(2.5, 2.5);
        ctx.lineTo(9.5, 9.5);
        ctx.moveTo(2.5, 9.5);
        ctx.lineTo(9.5, 2.5);
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = 'black';
        ctx.stroke();
*/

        form.disable_controls = function() {
          if (!this.disable_count) {
/*
            for (var i=0; i<this.obj_list.length; i++) {
              obj = this.obj_list[i];
              if (!obj.disable_count)
                obj.disabled = true;
              obj.disable_count += 1;
              };
*/
            if (this.header.currentStyle) //IE, Opera
              this.header.background = this.header.currentStyle['backgroundColor']
            else //others
              this.header.background =
                document.defaultView.getComputedStyle(this.header, "")['backgroundColor']
            this.header.style.background = 'lightgrey';
            };
          this.disable_count += 1;
          };

        form.enable_controls = function() {
          this.disable_count -= 1;
          if (!this.disable_count) {
/*
            for (var i=0; i<this.obj_list.length; i++) {
              obj = this.obj_list[i];
              obj.disable_count -= 1;
              if (!obj.disable_count)
                obj.disabled = false;
              };
*/
            this.header.style.background = this.header.background;
            };
          };

        form.req_cancel = function() {
          var args = [this.active_frame.ref];
          send_request('req_cancel', args);
          };

        form.req_close = function() {
          var args = [form.form_id + '_0'];  // the 'ref' of the main frame
          send_request('req_close', args);
          };

        form.onkeydown = function(e) {
          if (form.disable_count)
            return;
          if (!e) e=window.event;
          if (e.keyCode === 9) {  // user pressed Tab
            if (e.shiftKey)
              form.tabdir = -1
            else
              form.tabdir = 1;
            return;
            };
          if (e.keyCode === 13) {  // user pressed Enter
            if (ignore_enter)
              return;
            if (form.active_frame.active_button === undefined)
              return;
            // if user holds down Enter key, testing click_from_kbd
            //   prevents clicked() from being called multiple times
            // ignore_enter is set by a 'textarea' object, which uses
            //   'Enter' for new lines
            if (!click_from_kbd) {
              click_from_kbd = true;
              // don't know what problem this was supposed to solve [2014-04-23]
              // it causes problems [what problems? 2014-05-13]
              // e.g. login, input userid, <tab>, input password, <enter>
              // reverted back to original, and it works with IE8 and Chrome
//              form.active_frame.active_button.focus();
//              setTimeout(function() {form.active_frame.active_button.clicked()}, 0);

              // does not work [2014-05-13]
              // if we follow the above example, IE8 works, but Chrome and FF
              //   send [lost_focus, got_focus] in one 'packet', and [clicked]
              //   in a second 'packet'
              // result - 'clicked' is always processed, even if validation fails
              // i.e. we log in, even if the password is invalid!
              // the following code may be ugly, but it works correctly!

              // next bit is ugly!
              // IE delays effectively calls focus after timeout, which is too late
              // instead of setting focus on the active_button, we call got_focus()
              //   directly, which forces it to call active_button's got_focus()
              //   method immediately, which is what we want
              // it seems to work with IE and with Chrome [2013-08-07]
              //form.active_frame.active_button.focus();
//              got_focus(form.active_frame.active_button);
              //setTimeout(function() {form.active_frame.active_button.clicked()}, 0);
//              form.active_frame.active_button.clicked();
//              form.active_frame.active_button.after_focus =
//                form.active_frame.active_button.after_click;
//              form.active_frame.active_button.focus();
              form.active_frame.active_button.click();
              };
            e.cancelBubble = true;
            return false;
            };
          if (e.keyCode === 27) {  // Esc
            form.req_cancel();
            e.cancelBubble = true;
            return false;
            };
          if (e.keyCode === 115 && e.shiftKey) {  //  user pressed Shift+F4
            form.req_close();
            e.cancelBubble = true;
            return false;  // with Alt+F4 the main window is closed!
            };
          if (e.keyCode === 116) {  //  user pressed F5 - prevent refresh
            e.cancelBubble = true;
            e.keyCode = 0;
            return false;
            };
          };

        document.onkeyup = function(e) {
          if (!e) e=window.event;
          if (e.keyCode === 13) {  // user released Enter
            if (!ignore_enter) {  // never true - document.body!
              click_from_kbd = false;
              e.cancelBubble = true;
              return false;
              };
            };
          };

        form.close_form = function() {
          document.body.removeChild(this);
          this.root.splice(this.root.length-1, 1);  // remove last entry

//          for (var i=0; i<this.css_classes.length; i++)
//            delCSSClass(this.css_classes[i]);
          var i = this.css_classes.length;
          while (i--)
            delCSSClass(this.css_classes[i]);

          if (this.root.length) {
            current_form = this.root[this.root.length-1];
            current_form.enable_controls();
            setTimeout(function() {current_form.current_focus.focus()}, 50);
            //current_form.current_focus.focus();  // IE8 seems to lose focus otherwise!
            }
          else {
            delete active_roots[this.root_id];

            var old_pos = form.root.zindex;
            root_zindex.splice(old_pos, 1);
            for (var i=old_pos, z_length=root_zindex.length; i<z_length; i++) {
              var root = root_zindex[i];
              root.zindex = i;
              for (var j=0, root_length=root.length; j<root_length; j++)
                root[j].style.zIndex = (i*100) + j;
              };
            if (root_zindex.length)
              root_zindex[root_zindex.length-1][0].current_focus.focus()
            else if (menu !== null)
              menu.focus();
            };
          };

/*
        form.set_gridframe_border = function(frame) {
          // called from got_focus() if active_frame changes

          if (this.active_frame.default_button !== undefined)
            this.active_frame.default_button.style.border = '1px solid darkgrey';

          if (this.active_frame.type === 'grid_frame') {
            // clear border of current active_frame
            this.active_frame.page.style.border = '1px solid darkslategrey';
            //this.active_frame.ctrl_grid.parentNode.style.border = '1px solid transparent';
            this.active_frame.ctrl_grid.unhighlight_active_row();
            };

          if (frame.default_button !== undefined)
            frame.default_button.style.border = '1px solid blue';

          if (frame.type === 'grid_frame') {
            frame.page.style.border = '1px solid blue';
            //frame.ctrl_grid.parentNode.style.border = '1px solid blue';
            frame.ctrl_grid.highlight_active_row();
            var frame_amended = (frame.ctrl_grid.inserted !== 0);
            var set_focus = false;
            var args = [frame.ref, frame_amended, set_focus];
            start_frame(args);
            };
          };
*/

        break;

        };
      case 'frame': {
        var page = create_page();
        form.appendChild(page);

        var frame = {}  // new Object()
        frame.type = 'frame';  // to distinguish from 'grid_frame'
        frame.obj_list = [];
        frame.subtypes = {};  //new Object();
//        form.obj_list.push(frame);

        frame.ref = elem[1].ref;
        frame.form = form;
        frame.page = page;
        page.frame = frame;
        form.obj_dict[frame.ref] = frame;
        form.active_frame = frame;
        frame.frame_amended = false;
        frame.send_focus_msg = true;  // can be over-ridden in 'start_frame'

        if (elem[1].ctrl_grid_ref === null)
          frame.ctrl_grid = null;
        else
          frame.ctrl_grid = get_obj(elem[1].ctrl_grid_ref);

        frame.set_value_from_server = function(value) {
          this.frame_amended = value;
          };

        break;
        };
      case 'form_toolbar': {
        var toolbar = document.createElement('div');
        toolbar.style.clear = 'left';
        toolbar.style.marginTop = '10px';
        page.appendChild(toolbar);
        toolbar.frame = frame;
        create_frame_toolbar(toolbar, elem[1]);
        break;
        };
      case 'block': {
        var vbox = null;
        if (page.block != null)
          page.block.end_block();
        //var block = document.createElement('div');
        //page.appendChild(block);
//        var block = page.insertRow(page.row_no);
        var block = document.createElement('div');
        page.appendChild(block);
        block.style.clear = 'left';
        block.style.textAlign = 'center';
        page.block = block;
        block.end_block = function() {
          if (this.childNodes.length === 1)
            this.firstChild.style[cssFloat] = 'none';
//          if (this.children.length == 1) {
//            this.firstChild.style.display = 'block';
////            }
////          else {
////            var max = 0;
////            for (var j=0; j<this.children.length; j++) {
////              var height = this.children[j].offsetHeight;
////              if (height > max) max = height;
////              };
////            max -= 2;  // adjust for borders
////            for (var j=0; j<this.children.length; j++)
////              this.children[j].style.height = max + 'px';
//            };
          for (var j=0, child_length=this.childNodes.length; j<child_length; j++) {
            var child = this.childNodes[j];
            if (child.col_css !== undefined) {  // not every child is a panel
              for (var k=0, colcss_length=child.col_css.length; k<colcss_length; k++) {
                css_obj = child.col_css[k];
                if (css_obj !== undefined) {  // not every column has a css_obj
                  var text_rule = getCSSClass(css_obj[0]);
                  text_rule.style.width = css_obj[1] + 'px';
                  };
                };
              };
            };
          };
        break;
        };
      case 'vbox': {
        var vbox = document.createElement('div');
        vbox.style.textAlign = 'center';
        if (block.childNodes.length)
          vbox.style.marginLeft = '10px';
        block.appendChild(vbox);
        vbox.style[cssFloat] = 'left';
        break;
        };
      case 'vbox_end': {
        vbox = null;
        break;
        };
      case 'string': {
        var text = document.createElement('span');
        text.appendChild(document.createTextNode(elem[1].value));
        text.style[cssFloat] = 'left';
        text.style.textAlign = 'left';
        text.style.marginTop = '10px';
        if (elem[1].lng)
          text.style.width = elem[1].lng + 'px'
        block.appendChild(text);
        break;
        };
      case 'panel': {
        var box = document.createElement('div');
        box.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(box)
        else {
          if (block.childNodes.length && subtype_name === null)
            box.style.marginLeft = '10px';
          block.appendChild(box);
          // if a subtype panel, there are > 1 but only one is visible
          // for some reason, if they are floated, it prevents the following
          //    block from having a top margin
          // avoiding the float fixes it, but I think it means that you cannot
          //    have a subtype panel side-by-side with another panel
          // if this is required, experiment with another layer, with the
          //    outer layer floated, and the inner one with multiple divs
          if (subtype_name === null)
            box.style[cssFloat] = 'left';
          };

        var panel = document.createElement('span');
        panel.style.display = 'inline-block';
        box.appendChild(panel);
        //box.style.textAlign = 'center';
        panel.style.textAlign = 'left';
        box.style.border = '1px solid lightgrey';
        //panel.style.border = '1px solid lightgrey';
        //
        // which is better - set the border on the box or the panel?
        // 'box border' works better for subtype_frames - each subframe is the same size
        // if it is changed back to 'panel border', must change width adjustment
        //    for subframes - do *not* adjust by 2 for borders

//        var panel = document.createElement('table');
//        panel.style.borderSpacing = '10px';
//        box.appendChild(panel);

        var table = document.createElement('table');
        table.style.borderSpacing = '10px';
        panel.appendChild(table);
//        panel.style.background = 'lightgreen';

        if (subtype_name !== null) {
          var subtype = frame.subtypes[subtype_name];
          subtype[elem[1].subtype_id] = box;
          if (elem[1].active === true)
            subtype._active_box = elem[1].subtype_id;
          };
        break;
        };
      case 'row': {
        var row = table.insertRow(-1);
        break;
        };
      case 'col': {
        var col = row.insertCell(-1);
        if (elem[1].colspan)
          col.colSpan = elem[1].colspan;
        if (elem[1].rowspan)
          col.rowSpan = elem[1].rowspan;
        break;
        };
      case 'text': {
        var text = document.createElement('span');
        text.appendChild(document.createTextNode(elem[1].value));
        if (col.childNodes.length)
          text.style.marginLeft = '5px';
        col.appendChild(text);
        break;
        };
      case 'label': {
        var label = document.createElement('span');
        label.appendChild(document.createTextNode(elem[1].value));
        label.style[cssFloat] = 'left';
        label.style.cursor = 'default';
        if (col.childNodes.length)
          label.style.marginLeft = '5px';
        col.appendChild(label);
        break;
        };
      case 'input': {
        var input = create_input(frame, elem[1], label);
        if (col.childNodes.length)
          input.style.marginLeft = '5px';
        col.appendChild(input);
        var label = null;
        break;
        };
      case 'display': {
        var display = create_display(frame, elem[1]);
        if (col.childNodes.length)
          display.style.marginLeft = '5px';
        col.appendChild(display);
        break;
        };
      case 'dummy': {
        var dummy = create_input(frame, elem[1]);
        page.appendChild(dummy);
        break;
        };
      case 'button_row': {
        var button_row = document.createElement('div');
        button_row.style.paddingTop = '10px';
        button_row.style.textAlign = 'right';
        button_row.style.clear = 'left';
        page.appendChild(button_row);
        for (var j=0, tot_buttons=elem[1].length; j<tot_buttons; j++) {
          var button = create_button(frame, elem[1][j][1]);
          button_row.appendChild(button);
          button.style.marginRight = '10px';
//          button_row.appendChild(button.parentNode);
//          // don't know why +4, but otherwise Chrome truncates 'Change password'
//          button.parentNode.style.width = (button.offsetWidth + 4) + 'px';
//          button.parentNode.style.height = button.offsetHeight + 'px';
//          button.parentNode.style.marginRight = '10px';
          };
        break;
        };
      case 'button': {
        var button = create_button(frame, elem[1]);
        if (col.childNodes.length)
          text.style.marginLeft = '5px';
        col.appendChild(button);
//        col.appendChild(button.parentNode);
//        button.parentNode.style.width = (button.offsetWidth + 4) + 'px';
//        button.parentNode.style.height = button.offsetHeight + 'px';
        break;
        };
      case 'nb_start': {
        var notebook = document.createElement('div');
        notebook.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(notebook)
        else {
          if (block.childNodes.length)
            notebook.style.marginLeft = '10px';
          block.appendChild(notebook);
          notebook.style[cssFloat] = 'left';
          };
//        notebook.style.textAlign = 'center';
//        notebook.style.position = 'relative';
        notebook.style.border = '1px solid lightgrey';
        notebook.tabs = document.createElement('div');
        notebook.appendChild(notebook.tabs);
        notebook.frame = frame;
        notebook.save_page = page;  // restore in nb_end
        notebook.req_new_page = function(new_pos, back) {
          if (this.frame.form.disable_count) return;
          var new_page = this.childNodes[new_pos];
          if (back)
            var new_focus = new_page.last_obj;
          else
            var new_focus = new_page.first_obj;
          if (back)
            this.frame.form.tabdir = -1;
          if (this.frame.frame_amended) {
            callbacks.push([this, this.after_new_page, new_pos, new_focus]);
            got_focus(new_focus);  // trigger 'got_focus', even though it hasn't!
            }
          else {
            this.after_new_page(new_pos, new_focus);
            };
          };
        notebook.after_new_page = function(new_pos, new_focus) {
          var current_page = this.childNodes[this.current_pos];
          current_page.style.display = 'none';
          var current_tab = this.tabs.childNodes[this.current_pos-1]
          current_tab.style.borderBottom = '1px solid lightgrey';
          current_tab.style.color = 'grey';
          var new_page = this.childNodes[new_pos];
          new_page.style.display = 'block';
          var new_tab = this.tabs.childNodes[new_pos-1];
          new_tab.style.borderBottom = '1px solid transparent';
          new_tab.style.color = 'black';
          this.current_pos = new_pos;
          new_focus.focus();
          };
        break;
        };
      case 'nb_page': {
        var tab = document.createElement('span');
        tab.style.display = 'inline-block';
        tab.style.height = '20px';
        tab.style.padding = '3px 0px';
        tab.style.fontWeight = 'bold';
        tab.style.color = 'grey';
        tab.style.borderBottom = '1px solid lightgrey';
        tab.style.textAlign = 'center';
        tab.style.cursor = 'default';
        tab.pos = notebook.tabs.childNodes.length;
        tab.appendChild(document.createTextNode(elem[1].label));
        tab.onclick = function() {
          var notebook = this.parentNode.parentNode;
          notebook.req_new_page(this.pos+1, false);
          };
        notebook.tabs.appendChild(tab);

        var nb_page = document.createElement('div');
        //nb_page.style.background = 'pink';
        var page = create_page();
        nb_page.appendChild(page);
        nb_page.page = page;
        nb_page.style.textAlign = 'center';
        page.style.textAlign = 'left';
        nb_page.frame = frame;
        page.frame = frame;
        nb_page.pos = notebook.childNodes.length;  // starts from 1, 0 is 'tabs'
        nb_page.first_obj = frame.obj_list.length;
        notebook.save_page.sub_pages.push(page);
        //page.style.background = 'lightcyan';
        var nb_btns = document.createElement('div');
        nb_btns.style.height = '24px';
        nb_page.appendChild(nb_btns);
        nb_page.btns = nb_btns;

        nb_page.onkeydown = function(e) {
          if (this.frame.form.disable_count) return false;
          if (!e) e=window.event;
          if (e.ctrlKey) {
            if (e.keyCode === 33) {  // page up
              if (this.pos > 1) {
                this.parentNode.req_new_page(this.pos-1, true)
                e.cancelBubble = true;
                return false;
                };
              }
            else if (e.keyCode === 34) {  // page down
              if (this.pos < (this.parentNode.childNodes.length - 1)) {
                this.parentNode.req_new_page(this.pos+1, false)
                e.cancelBubble = true;
                return false;
                };
              };
            };
          };

//        var button_row = document.createElement('div');
//        button_row.style.verticalAlign = 'bottom';
////        nb_page.appendChild(button_row);
//        nb_page.button_row = button_row;

        nb_page.create_btn = function(back) {
          var nb_btn = document.createElement('div');
          nb_btn.style.backgroundImage = 'url(' + (back ? iPrev_src : iNext_src) + ')';

          nb_btn.pos = frame.obj_list.length;
          frame.obj_list.push(nb_btn);
          nb_btn.frame = frame;
          nb_btn.nb_page = this;

          nb_btn.tabIndex = 0;
          nb_btn.style.width = '16px';
          nb_btn.style.height = '16px';
          nb_btn.style.border = '1px solid transparent';
          nb_btn.style.padding = '1px';
          nb_btn.style.margin = '2px';
          nb_btn.title = back ? 'Previous tab' : 'Next tab';

//          nb_btn.style.position = 'absolute';
//          nb_btn.style[back ? 'left' : 'right'] = '10px';
//          nb_btn.style.bottom = '10px';
          nb_btn.style[cssFloat] = back ? 'left' : 'right';
          this.btns.appendChild(nb_btn);

          nb_btn.onkeydown = function(e) {
            if (this.frame.form.disable_count) return false;
            if (!e) e=window.event;
            if (e.keyCode === 13) {  // Enter
              var next = (back ? this.nb_page.pos-1 : this.nb_page.pos+1)
              this.nb_page.parentNode.req_new_page(next, back)
              e.cancelBubble = true;
              return false;
             };
           };

          nb_btn.onfocus = function() {
            if (this.frame.form.disable_count) return;
            this.style.border = '1px solid grey'
            };
          nb_btn.onblur = function() {this.style.border = '1px solid transparent'};

          nb_btn.onclick = function(e) {
            if (this.frame.form.disable_count) return false;
            var next = (back ? this.nb_page.pos-1 : this.nb_page.pos+1)
            this.nb_page.parentNode.req_new_page(next, back)
            };
          };

        nb_page.end_nb_page = function() {
//          this.button_row.style.clear = 'left';
//          this.appendChild(this.button_row);
          this.first_obj = frame.obj_list[this.first_obj];
          var last_obj = frame.obj_list.length - 1;
          while (frame.obj_list[last_obj].tabIndex === -1)
            last_obj -= 1;  // look for prev enabled object
          this.last_obj = frame.obj_list[last_obj];
          };

        if (notebook.childNodes.length > 1) {
          notebook.lastChild.end_nb_page();
          notebook.lastChild.create_btn(false);
          nb_page.create_btn(true);
          nb_page.first_obj += 2;
          };
        notebook.appendChild(nb_page);
        break;
        };
      case 'nb_end': {
        debug4('here');  // IE8 bug - form_setup_gui too narrow - this fixes it!
        notebook.lastChild.end_nb_page();

//      next bit is dodgy!
//      the theory is that, at this point, notebook.offsetWidth is equal
//        to the widest nb_page.page + 2
//      we then set 'display' to 'none' on all pages except the first one
//      notebook.offsetWidth will be reduced accordingly (unless the first
//        page is also the widest one)
//      so when the form is displayed, it is sized using the first page
//      if we move to a wider page, the form size is automatically adjusted
//      this is clever, but not ideal, because -
//        1. the size of the form jumps about as you switch pages
//        2. the wider form is no longer centered - the left margin stays in place
//      the answer is to set notebook.style.width to (max_wd+2), which freezes it
//      but we do *not* want to do this if form.offsetWidth is wider than the notebook
//      without it, notebook will expand to fill the space create by the form
//      with it, notebook will stay at the frozen (smaller) size
//      nb_page.page is centered within nb_page, which is centered within notebook
//      if notebook is smaller than form, nb_page.page is not centered in the form
//      to return to the theory, at this point, notebook.offsetWidth is equal
//        to the widest nb_page.page + 2
//      if the notebook is the widest element on the form, form.offsetWidth is equal
//        to notebook.offsetWidth + 24 (padding + border?), else it will be greater,
//        but it will never be less (I think)
//      so if the notebook is the widest element, it is safe to freeze the width,
//        otherwise it is not
//      it all depends on the value of 24 - not sure if it is guaranteed
//
//      OOPS - this will not work if the form becomes wider after the notebook
//        is set up
//      so all this should be done at the end when the form is complete!

//      if (form.offsetWidth - max_wd === 26)
//        notebook.style.width = (max_wd+2) + 'px';
//
// OR (if this works, we don't need max_wd at all)
//

//      this has not been thought through!
        if (notebook.frame.type === 'grid_frame')
          var max_gap = 46;
        else
          var max_gap = 24;

        if (form.offsetWidth - notebook.offsetWidth === max_gap)
          notebook.style.width = notebook.offsetWidth + 'px';

        var max_ht = max_wd = 0;
        for (var j=1, child_length=notebook.childNodes.length; j<child_length; j++) {
          var nb_page = notebook.childNodes[j];
          if (nb_page.offsetHeight > max_ht)
            max_ht = nb_page.offsetHeight;
          //if (nb_page.offsetWidth > max_wd)
          //  max_wd = nb_page.offsetWidth;
          };
        for (var j=1, child_length=notebook.childNodes.length; j<child_length; j++) {
          var nb_page = notebook.childNodes[j];
          nb_page.style.height = max_ht + 'px';
          };

        var no_tabs = notebook.tabs.childNodes.length;
        var tot = 100;
        var tab_perc = Math.floor((1 / no_tabs * 100));

        for (var j=(no_tabs-1); j>=0; j--) {
          var tab = notebook.tabs.childNodes[j];
          if (j === 0) {
            tab.style.width = tot + '%';
            tab.style.borderBottom = '1px solid transparent';
            tab.style.color = 'black';
            }
          else {
            notebook.childNodes[j+1].style.display = 'none';
            tab.style.borderLeft = '1px solid lightgrey';
            tab.style.marginLeft = '-1px';  // to keep width the same
            tab.style.width = tab_perc + '%';
            tot -= tab_perc;
            };
          };
        notebook.current_pos = 1;  // 0 = 'tabs', 1 = first nb_page
        var page = notebook.save_page;
        notebook.save_page = null;
        break;
        };
      case 'grid': {
        var box = document.createElement('div');
        box.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(box)
        else {
          if (block.childNodes.length)
            box.style.marginLeft = '10px';
          block.appendChild(box);
          box.style[cssFloat] = 'left';
          };
        var main_grid = document.createElement('span');
        main_grid.style.display = 'inline-block';
        box.appendChild(main_grid);
        //box.style.textAlign = 'center';
        main_grid.style.textAlign = 'left';
        create_grid(frame, main_grid, elem[1], elem[2]);
        break;
        };
      case 'grid_toolbar': {
        main_grid.create_grid_toolbar(elem[1]);
        var toolbar = main_grid.childNodes[0];
        var grid = main_grid.childNodes[1];
        var diff = toolbar.offsetWidth - grid.offsetWidth;
        if (diff > -20)  // initial size of row_count is based on '0/0'
          diff += 20;  // this allows for extra digits - very arbitrary!
        if (diff > 0)
          grid.change_size(diff);
        else
          toolbar.style.width = (grid.offsetWidth-2) + 'px';
        break;
        };
      case 'grid_frame': {
        save_pages.push(page);
        save_frames.push(frame);
        save_blocks.push(block);

        var page = create_page();
        page.style.border = '1px solid darkslategrey';
        page.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(page)
        else {
          if (block.childNodes.length)
            page.style.marginLeft = '10px';
          block.appendChild(page)
          page.style[cssFloat] = 'left';
          };

        save_vbox.push(vbox);
        vbox = null;

        var frame = {}  // new Object()
        frame.type = 'grid_frame';
        frame.obj_list = [];
        frame.subtypes = {};  //new Object();

        frame.ref = elem[1].ref;
        frame.form = form;
        frame.page = page;
        page.frame = frame;
        form.obj_dict[frame.ref] = frame;
        frame.frame_amended = false;
        frame.send_focus_msg = true;  // can be over-ridden in 'start_frame'

        frame.ctrl_grid = get_obj(elem[1].ctrl_grid_ref);
        frame.ctrl_grid.grid_frame = frame;
        frame.ctrl_grid.active_frame = frame;  // override grid's active_frame
        frame.ctrl_grid.parentNode.style.border = '1px solid transparent';

        frame.set_value_from_server = function(value) {
          this.frame_amended = value;
          this.ctrl_grid.row_amended = value;
          };

        break;
        };
      case 'grid_frame_end': {
        frame.page.end_page();
        var page = save_pages.pop();
        var frame = save_frames.pop();
        var block = save_blocks.pop();
        var vbox = save_vbox.pop();
        break;
        };
      case 'tree': {
        var box = document.createElement('div');
        box.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(box)
        else {
          if (block.childNodes.length)
            box.style.marginLeft = '10px';
          block.appendChild(box);
          box.style[cssFloat] = 'left';
          };
        box.style.width = elem[1].lng + 'px';
        box.style.height = elem[1].height + 'px';
        box.style.border = '1px solid grey';
        // store box.height for tree.js, so it knows when to overflow
        box.height = box.offsetHeight;

        var toolbar=elem[1].toolbar, tree_data = elem[1].tree_data, hide_root=false;
        for (var j=0, lng=tree_data.length; j<lng; j++) {
          var arg = tree_data[j];
          var node_id=arg[0], parent_id=arg[1], text=arg[2], expandable=arg[3];
          if (j === 0) {
            var tree = create_tree(box, frame, toolbar, hide_root);
            tree.ref = elem[1].ref
            frame.obj_list.push(tree);
            frame.form.obj_dict[tree.ref] = tree;
            };
          tree.add_node(parent_id, node_id, expandable, text, (j===0));
          };
        tree.onselected = function(node) {
          };
        tree.onactive = function(node) {
          var args = [tree.ref, node.node_id];
          send_request('treeitem_active', args);
          };
        tree.write();

        break;
        };
      case 'tree_frame': {
        save_pages.push(page);
        save_frames.push(frame);
        save_blocks.push(block);

        var page = create_page();
        page.style.border = '1px solid darkslategrey';
        page.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(page)
        else {
          if (block.childNodes.length)
            page.style.marginLeft = '10px';
          block.appendChild(page)
          page.style[cssFloat] = 'left';
          };

        save_vbox.push(vbox);
        vbox = null;

        var frame = {}  // new Object()
        frame.type = 'tree_frame';
        frame.obj_list = [];
        frame.subtypes = {};  //new Object();

        frame.ref = elem[1].ref;
        frame.form = form;
        frame.page = page;
        page.frame = frame;
        form.obj_dict[frame.ref] = frame;
        frame.frame_amended = false;
        frame.send_focus_msg = true;  // can be over-ridden in 'start_frame'

//        frame.ctrl_grid = get_obj(elem[1].ctrl_grid_ref);
//        frame.ctrl_grid.grid_frame = frame;
//        frame.ctrl_grid.active_frame = frame;  // override grid's active_frame
//        frame.ctrl_grid.parentNode.style.border = '1px solid transparent';
        frame.ctrl_grid = null;
        tree.tree_frame = frame;

        frame.set_value_from_server = function(value) {
          this.frame_amended = value;
//          this.ctrl_grid.row_amended = value;
          };

        break;
        };
      case 'tree_frame_end': {
        frame.page.end_page();
        var page = save_pages.pop();
        var frame = save_frames.pop();
        var block = save_blocks.pop();
        var vbox = save_vbox.pop();
        break;
        };
      case 'start_subtype': {
        subtype_name = elem[1];
        var subtype = {};  //new Object();
        subtype._active_box = null;
        frame.subtypes[subtype_name] = subtype;
        break;
        };
      case 'end_subtype': {
        var subtype = frame.subtypes[subtype_name];
        var max_subtype_w=0, max_subtype_h=0;
        for (var subtype_id in subtype) {
          if (subtype_id !== '_active_box') {
            var subtype_box = subtype[subtype_id];
            if (subtype_box.offsetWidth > max_subtype_w)
              max_subtype_w = subtype_box.offsetWidth;
            if (subtype_box.offsetHeight > max_subtype_h)
              max_subtype_h = subtype_box.offsetHeight;
            };
          };
        max_subtype_w -= 2;  // offsetWidth/Height includes borders
        max_subtype_h -= 2;  // style.width/height excludes borders
        for (var subtype_id in subtype) {
          if (subtype_id !== '_active_box') {
            var subtype_box = subtype[subtype_id];
            subtype_box.style.width = max_subtype_w + 'px';
            subtype_box.style.height = max_subtype_h + 'px';
            subtype_box.style.display = 'none';
            };
          };
        subtype[subtype._active_box].style.display = 'block';
        subtype_name = null;
        break;
        };
      };
    };

  var help_msg = document.createElement('div');
  page.appendChild(help_msg);
  help_msg.appendChild(document.createTextNode(''));
  help_msg.style.clear = 'left';
  help_msg.style.padding = '10px';
  help_msg.style.height = '18px';
  form.help_msg = help_msg.firstChild;

  frame.page.end_page();

  var max_x = (max_w - form.offsetWidth);
  var max_y = (max_h - form.offsetHeight);
  form.style.left = (max_x / 2) + 'px';
  form.style.top = (max_y / 4) + 'px';

  Drag.init(header, form, 0, max_x, 0, max_y);
  form.onDragStart = function(x, y) {
    if (form.root !== root_zindex[root_zindex.length-1]) {
      var old_pos = form.root.zindex;
      var new_pos = root_zindex.length-1;
      root_zindex.splice(new_pos, 0, root_zindex.splice(old_pos, 1)[0]);
      for (var i=old_pos; i<= new_pos; i++) {
        var root = root_zindex[i];
        root.zindex = i;
        for (var j=0, root_length=root.length; j<root_length; j++)
          root[j].style.zIndex = (i*100) + j;
        };
      };
    return true;
    };
  form.onDragEnd = function(x, y) {
    form.current_focus.focus();
    };

  };
