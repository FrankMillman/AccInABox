active_roots = {};  //new Object();
root_zindex = [];  //new Array();
current_form = null;
// next 2 must be global, because 'parent' can change between 'press' and 'release'
click_from_kbd = false;  // prevent keydown repeat
ignore_enter = false;  // allow 'enter' from textarea

function setup_form(args) {
  //debug3(JSON.stringify(args));

  var save_pages = [];
  var save_frames = [];
  var save_blocks = [];
  var save_vbox = [];
  var subtype_names = [];
  var label = null;
  var notebook = null;  // to detect if we are on a notebook page
  var last_parent = null;  // keep track of last parent to decide where to append 'dummy'

  var finrpt = false;

  // for (var elem of args) {  // v. cute, but does not work with Galaxy Note 2
  for (var i=0, args_length=args.length; i<args_length; i++) {
    var elem = args[i];
    var [elem_type, elem_args] = elem;  // NB 'grid' uses elem[2] for col_defns
    switch(elem_type) {
      case 'root':
        var root_id = elem_args.root_id;
        var root = [];  // can contain multiple forms
        active_roots[root_id] = root;
        root.zindex = root_zindex.length;
        root_zindex.push(root);
        break;
      case 'form':
        var form_id = elem_args.form_id;
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
        form.readonly = elem_args.readonly;

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

        header.appendChild(document.createTextNode(elem_args.title));
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
          if (this.current_focus.num_cols !== undefined)  // i.e. it must be a grid
            var args = [this.current_focus.ref];
          else
            var args = [this.active_frame.ref];
          send_request('req_close', args);
          };

        form.onkeydown = function(e) {
          if (form.disable_count)
            return;
          if (!e) e=window.event;
          if (e.key === 'Tab') {
            if (e.shiftKey)
              form.tabdir = -1
            else
              form.tabdir = 1;
            return;
            };
          if (e.key === 'Enter') {
            // ignore_enter is set by a 'textarea' object, which uses
            //   'Enter' for new lines
            if (ignore_enter)
              return;
            if (form.readonly)
              return;
            if (form.active_frame.active_button === undefined)
              return;
            if (form.active_frame.active_button.readonly)
              return;
            // if user holds down Enter key, testing click_from_kbd
            //   prevents clicked() from being called multiple times
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
          if (e.key === 'Escape') {
            form.req_cancel();
            e.cancelBubble = true;
            return false;
            };
          if (e.key === 'F4' && e.shiftKey) {
            form.req_close();
            e.cancelBubble = true;
            return false;  // with Alt+F4 the main window is closed!
            };
          if (e.key === 'F5') {  //  user pressed F5 - prevent refresh
            e.cancelBubble = true;
            return false;
            };
          };

        document.onkeyup = function(e) {
          if (!e) e=window.event;
          if (e.key === 'Enter') {
            if (!ignore_enter) {
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
            if (current_form.current_focus !== null)  // can be if called from on_start_form
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
        break;
      case 'frame':
        var page = create_page();
        form.appendChild(page);

        var frame = {}  // new Object()
        frame.type = 'frame';  // to distinguish from 'grid_frame'
        frame.obj_list = [];
        frame.subtypes = {};  //new Object();
//        form.obj_list.push(frame);

        frame.ref = elem_args.ref;
        frame.form = form;
        frame.page = page;
        page.frame = frame;
        form.obj_dict[frame.ref] = frame;
        form.active_frame = frame;
        frame._amended = false;
        frame.obj_exists = false;
        frame.err_flag = false;

        if (elem_args.ctrl_grid_ref === null)
          frame.ctrl_grid = null;
        else
          frame.ctrl_grid = get_obj(elem_args.ctrl_grid_ref);

        frame.set_amended = function(state) {
          //debug3('fset1 ' + this.ref + ' ' + state);
          this._amended = state;
          };

        frame.amended = function() {
          return this._amended;
          };

        frame.set_value_from_server = function(args) {
          // notification of record becoming clean/dirty (true/false)
//          if (value === true) {
//            this.obj_exists = true;
//            this.set_amended(false);
//            }
//          else {
//            this.set_amended(true);
//            };
          var clean = args[0], exists = args[1];
          this.set_amended(!clean);  // if clean, amended=false, if dirty, amended=true
          this.obj_exists = exists;
          var current_focus = this.form.current_focus;
          if (current_focus !== null) {
            if (current_focus.amendable !== undefined) {
              if (!current_focus.amendable())
                current_focus.className = 'readonly_background'
              else if (current_focus.frame.err_flag)  // would we ever get here? does no harm
                current_focus.className = 'error_background'
              else
                current_focus.className = 'focus_background';
              };
            };
          };
        break;
      case 'form_toolbar':
        var toolbar = document.createElement('div');
        toolbar.style.clear = 'left';
        toolbar.style.marginTop = '10px';
        page.appendChild(toolbar);
        toolbar.frame = frame;
        create_frame_toolbar(toolbar, elem_args);
        break;
      case 'block':
        var vbox = null;
        if (page.block != null)
          page.block.end_block();
        var block = document.createElement('div');
        page.appendChild(block);
        block.style.clear = 'left';
        block.style.textAlign = 'center';
        page.block = block;
        last_parent = block;

        block.end_block = function() {
          if (this.childNodes.length === 1)
            this.firstChild.style[cssFloat] = 'none';
//          if (this.children.length === 1) {
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
      case 'vbox':
        var vbox = document.createElement('div');
        vbox.style.textAlign = 'center';
        if (block.childNodes.length)
          vbox.style.marginLeft = '10px';
        block.appendChild(vbox);
        vbox.style[cssFloat] = 'left';
        break;
      case 'vbox_end':
        vbox = null;
        break;
      case 'string':
        var text = document.createElement('span');
        text.style.display = 'inline-block';
        text.appendChild(document.createTextNode(elem_args.value));
        text.style.fontWeight = 'bold';
        text.style.textAlign = 'left';
        text.style.marginTop = '10px';
        if (elem_args.lng)
          text.style.width = elem_args.lng + 'px'
        if (vbox !== null)
          vbox.appendChild(text)
        else {
          if (block.childNodes.length && !subtype_names.length)
            text.style.marginLeft = '10px';
          text.style[cssFloat] = 'left';
          block.appendChild(text);
          };
        break;
      case 'panel':
        var box = document.createElement('div');
        box.style.marginTop = '10px';
        if (vbox !== null)
          vbox.appendChild(box)
        else {
          if (block.childNodes.length && !subtype_names.length)
            box.style.marginLeft = '10px';
          block.appendChild(box);
          box.style[cssFloat] = 'left';
          };

        var panel = document.createElement('span');
        panel.style.display = 'inline-block';
        box.appendChild(panel);
        //box.style.textAlign = 'center';
        panel.style.textAlign = 'left';
        if (!subtype_names.length)
          box.style.border = '1px solid lightgrey';
        else
          box.style.width = '100%';  // ensure all panels same width [setup_ledg_periods]
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
        last_parent = table;
//        panel.style.background = 'lightgreen';
        break;
      case 'row':
        var row = table.insertRow(-1);
        break;
      case 'col':
        var col = row.insertCell(-1);
        if (elem_args.colspan)
          col.colSpan = elem_args.colspan;
        if (elem_args.rowspan)
          col.rowSpan = elem_args.rowspan;
        if (elem_args.align)
          col.style.textAlign = elem_args.align;
        break;
      case 'text':
        var text = document.createElement('span');
        text.appendChild(document.createTextNode(elem_args.value));
        text.style[cssFloat] = 'left';
        if (col.childNodes.length)
          text.style.marginLeft = '5px';
        col.appendChild(text);
        break;
      case 'label':
        var label = document.createElement('span');
        label.appendChild(document.createTextNode(elem_args.value));
        label.style[cssFloat] = 'left';
        label.style.cursor = 'default';
        if (col.childNodes.length)
          label.style.marginLeft = '5px';
        col.appendChild(label);
        break;
      case 'input':
        var input = create_input(frame, page, elem_args, label);
        if (col.childNodes.length)
          input.style.marginLeft = '5px';
        col.appendChild(input);
        var label = null;
        break;
      case 'display':
        var display = create_display(frame, elem_args, label);
        if (col.childNodes.length)
          display.style.marginLeft = '5px';
        col.appendChild(display);
        // next line is debatable [2018-10-07]
        // if label>display>input, (e.g. currency_id), we want label linked to input
        // removed for now - does this cause any problems?
        // var label = null;
        break;
      case 'dummy':
        var dummy = create_input(frame, page, elem_args, null);
        last_parent.appendChild(dummy);
        break;
      case 'button_row':
        var button_row = document.createElement('div');
        // button_row.style.paddingTop = '10px';
        button_row.style.textAlign = 'right';
        button_row.style.clear = 'left';
        page.appendChild(button_row);
        for (var j=0, tot_buttons=elem_args.length; j<tot_buttons; j++) {
          var btn_elem = elem_args[j];
          var button = create_button(frame, btn_elem[1]);
          button_row.appendChild(button);
          button.style.marginTop = '10px';
          button.style.marginRight = '10px';
          };
        break;
      case 'button':
        var button = create_button(frame, elem_args);
        if (col.childNodes.length)
          button.style.marginLeft = '5px';
        col.appendChild(button);
        break;
      case 'nb_start':
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
//          if (this.frame.amended()) {
//            callbacks.push([this, this.after_new_page, new_pos, new_focus]);
//            got_focus(new_focus);  // trigger 'got_focus', even though it hasn't!
//            }
//          else {
//            this.after_new_page(new_pos, new_focus);
//            };
//          };
//        notebook.after_new_page = function(new_pos, new_focus) {
          var current_page = this.childNodes[this.current_pos];
          current_page.style.display = 'none';
          var current_tab = this.tabs.childNodes[this.current_pos-1]
          current_tab.style.borderBottom = '1px solid lightgrey';
          current_tab.style.color = 'lightgrey';
          var new_page = this.childNodes[new_pos];
          new_page.style.display = 'block';
          var new_tab = this.tabs.childNodes[new_pos-1];
          new_tab.style.borderBottom = '1px solid transparent';
          new_tab.style.color = 'black';
          this.current_pos = new_pos;
          //new_focus.focus();
          if (!this.frame.form.focus_from_server) {
            var pos = new_focus.pos;
            while (this.frame.obj_list[pos].offsetHeight === 0)
              pos += this.frame.form.tabdir;  // look for next available object
            this.frame.obj_list[pos].focus();
            };
          };
        frame.notebook = notebook;
        break;
      case 'nb_page':
        var notebook = frame.notebook;
        var tab = document.createElement('span');
        tab.style.display = 'inline-block';
        tab.style.height = '20px';
        tab.style.padding = '3px 0px';
        tab.style.fontWeight = 'bold';
        tab.style.color = 'lightgrey';
        tab.style.borderBottom = '1px solid lightgrey';
        tab.style.textAlign = 'center';
        tab.style.cursor = 'default';
        tab.pos = notebook.tabs.childNodes.length;
        tab.appendChild(document.createTextNode(elem_args.label));
        tab.onclick = function() {
          var notebook = this.parentNode.parentNode;
          notebook.req_new_page(this.pos+1, false);
          };
        notebook.tabs.appendChild(tab);
        var nb_page = document.createElement('div');
        notebook.appendChild(nb_page);

        //var back_btn_div = document.createElement('div');
        var back_btn_div = document.createElement('span');
        nb_page.appendChild(back_btn_div);
        back_btn_div.style.display = 'inline-block';
        back_btn_div.style.width = '25px';
        //back_btn_div.style[cssFloat] = 'left';
        //back_btn_div.style.background = 'blue';

        var page = create_page();
        nb_page.appendChild(page);
        //page.style[cssFloat] = 'left';
        page.style.verticalAlign = 'top';
        //page.style.background = 'lightcyan';
        //nb_page.style.background = 'green';

        //var fwd_btn_div = document.createElement('div');
        var fwd_btn_div = document.createElement('span');
        nb_page.appendChild(fwd_btn_div);
        fwd_btn_div.style.display = 'inline-block';
        fwd_btn_div.style.width = '25px';
        //fwd_btn_div.style[cssFloat] = 'right';
        //fwd_btn_div.style.background = 'blue';

        nb_page.label = elem_args.label;
        nb_page.page = page;
        page.nb_page = nb_page;
        nb_page.style.textAlign = 'center';
        page.style.textAlign = 'left';
        nb_page.frame = frame;
        page.frame = frame;
        nb_page.pos = tab.pos+1;  //notebook.childNodes.length-1;  // starts from 1, 0 is 'tabs'
        nb_page.first_obj_pos = frame.obj_list.length;
        notebook.save_page.nb_pages.push(page);

        nb_page.onkeydown = function(e) {
          if (this.frame.form.disable_count) return false;
          if (!e) e=window.event;
          if (e.ctrlKey) {
            if (e.key === 'PageUp') {
              if (this.pos > 1) {
                this.parentNode.req_new_page(this.pos-1, true)
                e.cancelBubble = true;
                return false;
                };
              }
            else if (e.key === 'PageDown') {
              if (this.pos < (this.parentNode.childNodes.length - 1)) {
                this.parentNode.req_new_page(this.pos+1, false)
                e.cancelBubble = true;
                return false;
                };
              };
            };
          };

        nb_page.create_btn = function(back, help_msg) {
          var nb_btn = document.createElement('div');
          this.childNodes[back ? 0 : 2].appendChild(nb_btn);
          nb_btn.style.backgroundImage = 'url(' + (back ? iPrev_src : iNext_src) + ')';
          nb_btn.style.position = 'relative';
          nb_btn.style.top = '50%';
          //nb_btn.style.transform = 'translateY(-50%)';

          nb_btn.pos = frame.obj_list.length;
          frame.obj_list.push(nb_btn);
          nb_btn.frame = frame;
          nb_btn.nb_page = this;

          nb_btn.tabIndex = 0;
          nb_btn.style.width = '16px';
          nb_btn.style.height = '16px';
          nb_btn.style.border = '1px solid transparent';
          nb_btn.style.margin = '2px';
          nb_btn.active_frame = this.frame;
          nb_btn.help_msg = help_msg;
          nb_btn.title = help_msg;

          nb_btn.onkeydown = function(e) {
            if (this.frame.form.disable_count) return false;
            if (!e) e=window.event;
            if (e.key === 'Enter') {
              var next = (back ? this.nb_page.pos-1 : this.nb_page.pos+1)
              this.nb_page.parentNode.req_new_page(next, back)
              e.cancelBubble = true;
              return false;
             };
           };

          nb_btn.onfocus = function() {
            if (this.frame.form.disable_count) return;
            this.style.border = '1px solid grey'
            // got_focus(this);
            };
          nb_btn.onblur = function() {this.style.border = '1px solid transparent'};
          // nb_btn.got_focus = function() {};
          // nb_btn.lost_focus = function() {return true};

          nb_btn.onclick = function(e) {
            if (this.frame.form.disable_count) return false;
            var next = (back ? this.nb_page.pos-1 : this.nb_page.pos+1)
            this.nb_page.parentNode.req_new_page(next, back)
            };
          };

        nb_page.end_nb_page = function() {
          this.first_obj = frame.obj_list[this.first_obj_pos];
          if (this.first_obj === undefined)  // use 'Back' button instead
            this.first_obj = frame.obj_list[this.first_obj_pos-1];
          var last_obj = frame.obj_list.length - 1;
          while (frame.obj_list[last_obj].tabIndex === -1)
            last_obj -= 1;  // look for prev enabled object
          this.last_obj = frame.obj_list[last_obj];
          };

        if (notebook.childNodes.length > 2) {
          var prev_page = notebook.childNodes[notebook.childNodes.length-2];
          prev_page.end_nb_page();
          prev_page.create_btn(false, 'Forward to ' + nb_page.label);
          nb_page.create_btn(true, 'Back to ' + prev_page.label);
          nb_page.first_obj_pos += 2;
          };
//        notebook.appendChild(nb_page);
        break;
      case 'nb_end':
        var notebook = frame.notebook;
        // obscure IE8 bug [2015-07-05]
        // if there is a grid, and we add a toolbar, we adjust the size of the grid
        // IE8 does not recalculate grid.offsetWidth immediately, and by the time
        //   it gets round to it, the nb_page is hidden, so it does not adjust
        //   the width of the notebook
        // for some reason, writing anything to the screen at this point enables
        //   it to recalculate grid.offsetWidth immediately (!)
        debug4('here');
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
          nb_page.firstChild.style.height = (max_ht - 2) + 'px';
          nb_page.lastChild.style.height = (max_ht - 2) + 'px';
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
        notebook = null;
        break;
      case 'grid':
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
        create_grid(frame, main_grid, page, elem_args, elem[2]);
        break;
      case 'grid_toolbar':
        main_grid.create_grid_toolbar(elem_args);
        var toolbar = main_grid.childNodes[0];
        var grid = main_grid.childNodes[1];
        var toolbar_width = toolbar.offsetWidth + 20  // allow for extra digits
        var diff = toolbar_width - grid.offsetWidth;
        if (diff > 0)
          grid.change_size(diff);
//        else
//          toolbar.style.width = (grid.offsetWidth-2) + 'px';
        break;
      case 'grid_frame':
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

        frame.ref = elem_args.ref;
        frame.form = form;
        frame.page = page;
        page.frame = frame;
        form.obj_dict[frame.ref] = frame;
        frame._amended = false;
        frame.obj_exists = false;
        frame.err_flag = false;

        frame.ctrl_grid = get_obj(elem_args.ctrl_grid_ref);
        frame.ctrl_grid.grid_frame = frame;
        frame.ctrl_grid.active_frame = frame;  // override grid's active_frame
        frame.ctrl_grid.parentNode.style.border = '1px solid transparent';
        frame.ctrl_grid.add_gridframe_indicator();

        // page.kbd_shortcuts = frame.ctrl_grid.kbd_shortcuts  // Ctrl_Ins & Ctrl_Del, if set up
        if (frame.ctrl_grid.kbd_shortcuts['ctrl']['Insert'] !== undefined)
          page.kbd_shortcuts['ctrl']['Insert'] = frame.ctrl_grid.kbd_shortcuts['ctrl']['Insert'];
        if (frame.ctrl_grid.kbd_shortcuts['ctrl']['Delete'] !== undefined)
          page.kbd_shortcuts['ctrl']['Delete'] = frame.ctrl_grid.kbd_shortcuts['ctrl']['Delete'];

        // assume grid_frame will always accept navigation keys
        page.nav = {}

        page.nav.top = {}
        page.nav.top.frame = page.frame;
        page.nav.top.onclick = function() {
          var frame = this.frame;
          if (frame.disable_count) return false;
          if (frame.ctrl_grid.active_row === 0)
            return;
          var args = [frame.ref, 'first'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          }
        page.kbd_shortcuts['ctrl']['Home'] = page.nav.top;

        page.nav.up = {}
        page.nav.up.frame = page.frame;
        page.nav.up.onclick = function() {
          var frame = this.frame;
          if (frame.disable_count) return false;
          if (frame.ctrl_grid.active_row === 0)
            return;
          var args = [frame.ref, 'prev'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          }
        page.kbd_shortcuts['ctrl']['ArrowUp'] = page.nav.up;

        page.nav.down = {}
        page.nav.down.frame = page.frame;
        page.nav.down.onclick = function() {
          var frame = this.frame;
          if (frame.disable_count) return false;
//          if (frame.ctrl_grid.active_row === (frame.ctrl_grid.total_rows()-1))
          if (frame.ctrl_grid.active_row === (frame.ctrl_grid.num_data_rows))
            return;
          var args = [frame.ref, 'next'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          }
        page.kbd_shortcuts['ctrl']['ArrowDown'] = page.nav.down;

        page.nav.end = {}
        page.nav.end.frame = page.frame;
        page.nav.end.onclick = function() {
          var frame = this.frame;
          if (frame.disable_count) return false;
//          if (frame.ctrl_grid.active_row === (frame.ctrl_grid.total_rows()-1))
          if (frame.ctrl_grid.active_row === (frame.ctrl_grid.num_data_rows))
            return;
          var args = [frame.ref, 'last'];
          send_request('navigate', args);
          frame.form.current_focus.focus();
          }
        page.kbd_shortcuts['ctrl']['End'] = page.nav.end;

        frame.set_amended = function(state) {
          //debug3('fset2 ' + this.ref + ' ' + state);
          this._amended = state;
          //if (state === true)
          ////  if (!this.ctrl_grid.amended())
          //    this.ctrl_grid.set_amended(true);
          };

        frame.amended = function() {
          return this._amended;
          };

        frame.set_value_from_server = function(args) {
          // notification of record becoming clean/dirty (true/false)
//          if (value === true) {
//            this.obj_exists = true;
//            this.set_amended(false);
//            this.ctrl_grid.set_amended(false);
//            }
//          else {
//            this.set_amended(true);
//            this.ctrl_grid.set_amended(true);
//            };
          var clean = args[0], exists = args[1];
          this.set_amended(!clean);  // if clean, amended=false, if dirty, amended=true
          this.ctrl_grid.set_amended(!clean);
          this.obj_exists = exists;
          };

        break;
      case 'grid_frame_end':
        frame.page.end_page();
        var page = save_pages.pop();
        var frame = save_frames.pop();
        var block = save_blocks.pop();
        var vbox = save_vbox.pop();
        break;
      case 'tree':
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
        box.style.width = elem_args.lng + 'px';
        box.style.height = elem_args.height + 'px';
        box.style.border = '1px solid grey';
        // store box.height for tree.js, so it knows when to overflow
        box.height = box.offsetHeight;

        var tree = create_tree(box, frame, page, elem_args.toolbar);
        tree.ref = elem_args.ref
        tree.pos = frame.obj_list.length;
        frame.obj_list.push(tree);
        frame.form.obj_dict[tree.ref] = tree;
        if (elem_args.lkup) {
          tree.select_any = true;
          tree.onselected = function(node) {
            var args = [tree.ref, node.node_id];
            send_request('treelkup_selected', args);
            };
          tree.onactive = function(node) {};
          }
        else {
          tree.onselected = function(node) {};
          tree.onactive = function(node) {
            var args = [tree.ref, node.node_id];
            send_request('treeitem_active', args);
            };
        };

        tree.combo = elem_args.combo;
        if (tree.combo !== null) {
          var group_name = tree.combo[0];
          var member_name = tree.combo[1];
          tree.tree_frames = {};  // store 'group' and 'member' frames
          };

        break;
      case 'tree_report':
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
        box.style.width = elem_args.lng + 'px';
        box.style.height = elem_args.height + 'px';
        box.style.border = '1px solid grey';
        // store box.height for tree.js, so it knows when to overflow
        box.height = box.offsetHeight;

        var tree = create_tree_report(box, frame, page);
        tree.ref = elem_args.ref
        frame.obj_list.push(tree);
        frame.form.obj_dict[tree.ref] = tree;

        tree.onactive = function(node) {};
        tree.onselected = function(node) {};
        break;
      case 'tree_frame':
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

        frame.ref = elem_args.ref;
        frame.form = form;
        frame.page = page;
        page.frame = frame;
        form.obj_dict[frame.ref] = frame;
        frame._amended = false;
        frame.obj_exists = false;
        frame.err_flag = false;

        if (elem_args.combo_type !== null) {
          frame.combo_type = elem_args.combo_type;
          tree.tree_frames[elem_args.combo_type] = frame;
          frame.tree = tree;
          };

//        frame.ctrl_grid = get_obj(elem_args.ctrl_grid_ref);
//        frame.ctrl_grid.grid_frame = frame;
//        frame.ctrl_grid.active_frame = frame;  // override grid's active_frame
//        frame.ctrl_grid.parentNode.style.border = '1px solid transparent';
        frame.ctrl_grid = null;
        tree.tree_frame = frame;

        frame.set_amended = function(state) {
          //debug3('fset3 ' + this.ref + ' ' + state);
          this._amended = state;
          };

        frame.amended = function() {
          return this._amended;
          };

        frame.set_value_from_server = function(args) {
          // notification of record becoming clean/dirty (true/false)
//          if (value === true) {
//            this.obj_exists = true;
//            this.set_amended(false);
//            }
//          else {
//            this.set_amended(true);
//            };
          var clean = args[0], exists = args[1];
          this.set_amended(!clean);  // if clean, amended=false, if dirty, amended=true
          this.obj_exists = exists;
          };

        break;
      case 'tree_frame_end':
        if (frame.combo_type !== undefined) {
          if (frame.combo_type === 'member') {
            var max_fw = frame.page.offsetWidth, max_fh = frame.page.offsetHeight;
            var group_frame = frame.tree.tree_frames['group'];
            if (group_frame.page.offsetWidth > max_fw)
              max_fw = group_frame.page.offsetWidth;
            if (group_frame.page.offsetHeight > max_fh)
              max_fh = group_frame.page.offsetHeight;
            frame.page.style.width = max_fw + 'px';
            frame.page.style.height = max_fh + 'px';
            group_frame.page.style.width = max_fw + 'px';
            group_frame.page.style.height = max_fh + 'px';
            frame.page.style.display = 'none';
            };
          };
        frame.page.end_page();

        var page = save_pages.pop();
        var frame = save_frames.pop();
        var block = save_blocks.pop();
        var vbox = save_vbox.pop();
        break;
      case 'subtype_start':
        save_pages.push(page);
        save_blocks.push(block);

        var subtype_div = document.createElement('span');
        subtype_div.style.display = 'inline-block';
        subtype_div.style.marginTop = '10px';

        // block.appendChild(subtype_div);
        if (vbox !== null)
          vbox.appendChild(subtype_div)
        else {
          if (block.childNodes.length)
            subtype_div.style.marginLeft = '10px';
          block.appendChild(subtype_div);
          subtype_div.style[cssFloat] = 'left';
          };

        subtype_div.style.border = '1px solid lightgrey';

        save_vbox.push(vbox);
        vbox = null;

        var subtype_name = elem_args;
        var subtype = {};  //new Object();
        subtype._active_subtype = null;
        subtype._subtype_div = subtype_div;
        frame.subtypes[subtype_name] = subtype;
        subtype_names.push(subtype_name);
        break;
      case 'subtype_frame':
        var subtype = frame.subtypes[subtype_names[subtype_names.length-1]];
        var subtype_div = subtype._subtype_div;
        var subtype_id = elem_args.subtype_id, active = elem_args.active;

        var page = create_page();
//        page.style.border = '1px solid darkslategrey';
//        page.style.marginTop = '10px';
        subtype_div.appendChild(page)
        page.style[cssFloat] = 'left';

        subtype[subtype_id] = page;
        if (active === true)
          subtype._active_subtype = subtype_id;
        break;

      case 'subtype_end':
        var subtype = frame.subtypes[subtype_names[subtype_names.length-1]];
        var subtype_div = subtype._subtype_div;
        var max_subtype_w=0, max_subtype_h=0;
        for (var subtype_id in subtype) {
          if (subtype_id.substring(0, 1) !== '_') {
            var subtype_page = subtype[subtype_id];
            if (subtype_page.offsetWidth > max_subtype_w)
              max_subtype_w = subtype_page.offsetWidth;
            if (subtype_page.offsetHeight > max_subtype_h)
              max_subtype_h = subtype_page.offsetHeight;
            };
          };
// causes problem with sls_report - don't know why [2016-03-06]
//      max_subtype_w -= 2;  // offsetWidth/Height includes borders
//      max_subtype_h -= 2;  // style.width/height excludes borders
        for (var subtype_id in subtype) {
          if (subtype_id.substring(0, 1) !== '_') {
            var subtype_page = subtype[subtype_id];
            subtype_page.style.width = max_subtype_w + 'px';
            subtype_page.style.height = max_subtype_h + 'px';
            subtype_page.style.display = 'none';
            };
          };
        subtype[subtype._active_subtype].style.display = 'block';

        subtype_div.style.width = max_subtype_w + 'px';
        subtype_div.style.height = max_subtype_h + 'px';

        var page = save_pages.pop();
        var block = save_blocks.pop();
        var vbox = save_vbox.pop();
        subtype_names.pop();
        break;

      case 'finrpt':
        setup_finrpt(frame, elem_args.ref, elem_args.args);
        finrpt = true;
        break;

      case 'bpmn':
        setup_bpmn(frame, elem_args.ref, elem_args.nodes, elem_args.edges);
        break;

      };
    };

  if (!finrpt) {
    var help_msg = document.createElement('div');
    page.appendChild(help_msg);
    help_msg.appendChild(document.createTextNode(''));
    help_msg.style.clear = 'left';
    help_msg.style.padding = '10px';
    help_msg.style.height = '18px';
    form.help_msg = help_msg.firstChild;
    };

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
