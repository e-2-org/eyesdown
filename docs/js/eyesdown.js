/*
 * eyes-down: the bingo card (card.html) and its topic windows
 *
 * The original opened each number's topic in a popup, and played its sounds
 * from Flash files in hidden frames. Here:
 *  - clicking a number calls it (audio/numbers/N.mp3), marks it on the card
 *    and opens its topic (topics/NN.json) in a window over the card. Windows
 *    open from the top left, can be dragged by their title bar (in the colour
 *    of the number's cell), and close with x or Escape
 *  - a topic shows one page at a time, as the popup did: click the picture,
 *    or the arrows (or the arrow keys), for the next page. Topics with
 *    sections have a contents list
 *  - sounds play where the original's did: on opening a topic (the film), on
 *    moving on from a page, from the jingles' list, and from Shaun Fox's
 *    recordings. A window's sound stops when it closes
 *  - marked numbers are kept in the browser; with all 30 marked: Bingo!
 *  - card.html#17 opens topic 17
 */
(function () {
	'use strict';

	var WIN_W = 582, WIN_H = 640;
	var STORE = 'eyesdown-marked';
	var card = document.getElementById('card');
	var newCard = document.getElementById('new-card');
	var wins = {};
	var zTop = 500;
	var opened = 0;
	var caller = new Audio();

	/* ---------- marked numbers ---------- */

	var marked = new Set();
	try {
		JSON.parse(localStorage.getItem(STORE) || '[]').forEach(function (n) { marked.add(n); });
	} catch (e) { /* storage unavailable */ }

	function cellOf(n) {
		return card.querySelector('[data-n="' + n + '"]');
	}

	function showMark(n) {
		var cell = cellOf(n);
		var img = cell.querySelector('img');
		img.dataset.src = img.dataset.src || img.getAttribute('src');
		img.src = marked.has(n) ? 'images/numbers/img' + n + '_on.gif' : img.dataset.src;
	}

	function save() {
		try {
			localStorage.setItem(STORE, JSON.stringify(Array.from(marked)));
		} catch (e) { /* storage unavailable */ }
		newCard.hidden = marked.size === 0;
	}

	function mark(n) {
		if (marked.has(n)) return;
		marked.add(n);
		showMark(n);
		save();
		if (marked.size === 30) setTimeout(bingo, 600);
	}

	marked.forEach(showMark);
	newCard.hidden = marked.size === 0;
	newCard.addEventListener('click', function () {
		var was = Array.from(marked);
		marked.clear();
		was.forEach(showMark);
		save();
		if (wins.bingo) closeWin(wins.bingo);
	});

	/* ---------- windows ---------- */

	function viewW() { return document.documentElement.clientWidth; }
	function viewH() { return document.documentElement.clientHeight; }
	function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

	function createWin(key, title, colour, w, h) {
		var win = document.createElement('section');
		win.className = 'win';
		win.setAttribute('role', 'dialog');
		win.setAttribute('aria-label', title);
		win.style.setProperty('--c', colour);
		win.innerHTML = '<header class="win-bar"><span class="win-title"></span>' +
			'<button type="button" class="win-close" aria-label="Close">&times;</button></header>' +
			'<div class="win-body"></div>';
		win.querySelector('.win-title').textContent = title;
		win._key = key;
		win._w = w;
		win._h = h;
		win._body = win.querySelector('.win-body');
		win._audio = new Audio();
		win.querySelector('.win-close').addEventListener('click', function () { closeWin(win); });
		win.addEventListener('pointerdown', function () { raise(win); });
		makeDraggable(win);
		document.body.appendChild(win);
		wins[key] = win;
		return win;
	}

	function raise(win) {
		win.style.zIndex = ++zTop;
	}

	// the content keeps its original size, scaled down to fit small screens
	function layoutWin(win) {
		var bar = win.querySelector('.win-bar').offsetHeight;
		var s = Math.min(1, (viewW() - 16) / win._w, (viewH() - 16 - bar) / win._h);
		win._body.style.width = Math.round(win._w * s) + 'px';
		win._body.style.height = Math.round(win._h * s) + 'px';
		var inner = win._body.firstElementChild;
		if (inner) inner.style.transform = s < 1 ? 'scale(' + s + ')' : '';
		var left, top;
		if (win._dragged) {
			left = win._left;
			top = win._top;
		} else if (viewW() >= 700 && s === 1) {
			// from the top left, each new window a little further in, as popups cascade
			left = win._cascade * 28 + 16;
			top = win._cascade * 28 + 16;
		} else {
			left = (viewW() - win._w * s) / 2;
			top = (viewH() - win._h * s - bar) / 2;
		}
		moveWin(win, left, top);
	}

	function moveWin(win, left, top) {
		win._left = clamp(left, 0, Math.max(0, viewW() - win.offsetWidth));
		win._top = clamp(top, 0, Math.max(0, viewH() - win.offsetHeight));
		win.style.left = Math.round(win._left) + 'px';
		win.style.top = Math.round(win._top) + 'px';
	}

	function showWin(win) {
		// small screens: one window at a time
		if (viewW() < 700) {
			Object.keys(wins).forEach(function (k) { if (wins[k] !== win) closeWin(wins[k]); });
		}
		if (!win.classList.contains('is-open')) {
			win._cascade = opened++ % 8;
			win._dragged = false;
		}
		layoutWin(win);
		raise(win);
		win.classList.add('is-open');
	}

	function closeWin(win) {
		if (!win.classList.contains('is-open')) return;
		win.classList.remove('is-open');
		stopSound(win);
		if (Object.keys(wins).every(function (k) { return !wins[k].classList.contains('is-open'); })) opened = 0;
	}

	function topWin() {
		var top = null;
		Object.keys(wins).forEach(function (k) {
			var w = wins[k];
			if (w.classList.contains('is-open') && (!top || +w.style.zIndex > +top.style.zIndex)) top = w;
		});
		return top;
	}

	function makeDraggable(win) {
		var bar = win.querySelector('.win-bar');
		var start = null;
		bar.addEventListener('pointerdown', function (e) {
			if (e.target.closest('button')) return;
			start = { x: e.clientX - win._left, y: e.clientY - win._top };
			bar.setPointerCapture(e.pointerId);
		});
		bar.addEventListener('pointermove', function (e) {
			if (!start) return;
			win._dragged = true;
			moveWin(win, e.clientX - start.x, e.clientY - start.y);
		});
		function end() { start = null; }
		bar.addEventListener('pointerup', end);
		bar.addEventListener('pointercancel', end);
	}

	window.addEventListener('resize', function () {
		Object.keys(wins).forEach(function (k) {
			if (wins[k].classList.contains('is-open')) layoutWin(wins[k]);
		});
	});

	/* ---------- sound ---------- */

	function playSound(win, src, button) {
		var a = win._audio;
		var same = a.dataset.src === src;
		if (same && !a.paused) {
			a.pause();
			setPlaying(win, null);
			return;
		}
		if (!same) {
			a.src = src;
			a.dataset.src = src;
		}
		a.currentTime = 0;
		a.play().catch(function () { /* blocked until the visitor has clicked */ });
		setPlaying(win, button);
		a.onended = function () { setPlaying(win, null); };
	}

	function stopSound(win) {
		win._audio.pause();
		setPlaying(win, null);
	}

	function setPlaying(win, button) {
		win.querySelectorAll('.is-playing').forEach(function (b) { b.classList.remove('is-playing'); });
		if (button) button.classList.add('is-playing');
	}

	/* ---------- topics ---------- */

	var topics = {};

	function loadTopic(n) {
		if (!topics[n]) {
			topics[n] = fetch('topics/' + String(n).padStart(2, '0') + '.json').then(function (r) {
				if (!r.ok) throw new Error(r.status + ' ' + r.url);
				return r.json();
			});
		}
		return topics[n];
	}

	function openTopic(n, call) {
		if (call) {
			caller.src = 'audio/numbers/' + n + '.mp3';
			caller.play().catch(function () {});
		}
		mark(n);
		var key = 'topic' + n;
		if (wins[key]) {
			var open = wins[key].classList.contains('is-open');
			showWin(wins[key]);
			if (!open) showPage(wins[key], 0, false);
			return;
		}
		loadTopic(n).then(function (t) {
			var win = createWin(key, t.number + ' ' + t.title, t.colour, WIN_W, WIN_H);
			win._topic = t;
			buildViewer(win);
			showWin(win);
			showPage(win, 0, false);
		});
	}

	function buildViewer(win) {
		var t = win._topic;
		var v = document.createElement('div');
		v.className = 'viewer';
		v.innerHTML = '<div class="stage"></div>' +
			'<div class="caption"><button type="button" class="nav prev" aria-label="Previous page">&lsaquo;</button>' +
			'<p class="caption-text" aria-live="polite"></p>' +
			'<button type="button" class="nav next" aria-label="Next page">&rsaquo;</button></div>';
		win._body.appendChild(v);
		win._stage = v.querySelector('.stage');
		win._caption = v.querySelector('.caption-text');
		v.querySelector('.prev').addEventListener('click', function () { showPage(win, win._page - 1, false); });
		v.querySelector('.next').addEventListener('click', function () { next(win); });
		if (t.sections) {
			var b = document.createElement('button');
			b.type = 'button';
			b.className = 'contents-button';
			b.textContent = 'contents';
			b.setAttribute('aria-expanded', 'false');
			var list = document.createElement('ul');
			list.className = 'contents';
			list.hidden = true;
			t.sections.forEach(function (s) {
				var li = document.createElement('li');
				var sb = document.createElement('button');
				sb.type = 'button';
				sb.textContent = s.title;
				sb.dataset.page = s.page - 1;
				sb.addEventListener('click', function () {
					showPage(win, s.page - 1, false);
					toggle(false);
				});
				li.appendChild(sb);
				list.appendChild(li);
			});
			function toggle(show) {
				list.hidden = !show;
				b.setAttribute('aria-expanded', String(show));
			}
			b.addEventListener('click', function () { toggle(list.hidden); });
			v.querySelector('.caption').append(b, list);
			win._contents = list;
		}
		if (t.sound) {
			win._audio.src = t.sound;
			win._audio.dataset.src = t.sound;
		}
	}

	function next(win) {
		if (win._page < win._topic.pages.length - 1) showPage(win, win._page + 1, true);
	}

	// show page i; "forward" is moving on from the page before, which is when the original played a page's sound
	function showPage(win, i, forward) {
		var t = win._topic;
		var p = t.pages[i];
		if (!p) return;
		win._page = i;
		var stage = win._stage;
		stage.style.setProperty('--bg', p.bg);
		stage.innerHTML = '';
		if (p.kind === 'picture') {
			var box = document.createElement('div');
			box.className = 'stage-picture' + (p.areas ? ' has-areas' : '');
			var img = document.createElement('img');
			img.src = p.img.src;
			img.width = p.img.width;
			img.height = p.img.height;
			img.alt = p.caption;
			box.appendChild(img);
			if (p.areas) {
				p.areas.forEach(function (a, k) {
					var b = document.createElement('button');
					b.type = 'button';
					b.className = 'area';
					b.style.left = a.box[0] / p.img.width * 100 + '%';
					b.style.top = a.box[1] / p.img.height * 100 + '%';
					b.style.width = a.box[2] / p.img.width * 100 + '%';
					b.style.height = a.box[3] / p.img.height * 100 + '%';
					if (a.next) {
						b.setAttribute('aria-label', 'Next page');
						b.addEventListener('click', function () { next(win); });
					} else {
						b.setAttribute('aria-label', 'Play jingle ' + (k + 1));
						b.addEventListener('click', function () { playSound(win, a.sound, b); });
					}
					box.appendChild(b);
				});
			} else {
				img.addEventListener('click', function () { next(win); });
			}
			stage.appendChild(box);
			if (p.recordings) {
				var ol = document.createElement('ol');
				ol.className = 'recordings';
				p.recordings.forEach(function (r) {
					var li = document.createElement('li');
					var rb = document.createElement('button');
					rb.type = 'button';
					rb.textContent = r.title;
					rb.addEventListener('click', function () { playSound(win, r.src, rb); });
					li.appendChild(rb);
					ol.appendChild(li);
				});
				stage.appendChild(ol);
			}
		} else {
			var text = document.createElement('div');
			text.className = 'stage-text';
			text.innerHTML = '<div class="stage-text-inner">' + p.html + '</div>';
			stage.appendChild(text);
		}
		win._caption.innerHTML = '';
		if (p.caption) {
			var c = document.createElement('span');
			c.textContent = p.caption;
			win._caption.appendChild(c);
		}
		var count = document.createElement('span');
		count.textContent = (i + 1) + '/' + t.pages.length;
		win._caption.appendChild(count);
		win.querySelector('.prev').disabled = i === 0;
		win.querySelector('.next').disabled = i === t.pages.length - 1;
		if (win._contents) {
			var current = 0;
			t.sections.forEach(function (s, k) { if (s.page - 1 <= i) current = k; });
			win._contents.querySelectorAll('button').forEach(function (b, k) {
				if (k === current) b.setAttribute('aria-current', 'true');
				else b.removeAttribute('aria-current');
			});
		}
		if (i === 0 && t.sound && !forward) {
			playSound(win, t.sound, null);
		} else if (p.sound && forward) {
			playSound(win, p.sound, null);
		} else if (p.recordings || p.areas) {
			stopSound(win);
		}
	}

	/* ---------- the full house ---------- */

	function bingo() {
		var win = wins.bingo;
		if (!win) {
			win = createWin('bingo', 'You’ve Won!', 'var(--pink)', 350, 214);
			var b = document.createElement('div');
			b.className = 'bingo';
			b.innerHTML = '<img src="images/bingo.jpg" width="350" height="170" alt="Bingo!">' +
				'<button type="button">Start a new card</button>';
			b.querySelector('button').addEventListener('click', function () { newCard.click(); });
			win._body.appendChild(b);
		}
		showWin(win);
		playSound(win, 'audio/prizewin.mp3', null);
	}

	/* ---------- events ---------- */

	card.addEventListener('click', function (e) {
		var a = e.target.closest('a[data-n]');
		if (!a || e.ctrlKey || e.metaKey || e.shiftKey) return;
		e.preventDefault();
		openTopic(+a.dataset.n, true);
	});

	document.addEventListener('keydown', function (e) {
		var win = topWin();
		if (!win) return;
		if (e.key === 'Escape') {
			if (win._contents && !win._contents.hidden) win.querySelector('.contents-button').click();
			else closeWin(win);
		} else if (win._topic && !e.target.closest('input, textarea')) {
			if (e.key === 'ArrowRight') next(win);
			else if (e.key === 'ArrowLeft') showPage(win, win._page - 1, false);
		}
	});

	function fromHash() {
		var n = parseInt(location.hash.slice(1), 10);
		if (n >= 1 && n <= 30) openTopic(n, false);
	}
	window.addEventListener('hashchange', fromHash);
	fromHash();
})();
