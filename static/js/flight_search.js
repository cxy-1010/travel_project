(function () {
	'use strict';

	var params = new URLSearchParams(window.location.search);
	var state = {
		from: params.get('from') || '北京',
		to: params.get('to') || '上海',
		departure: params.get('departure') || '',
		returnDate: params.get('return') || '',
		adults: params.get('adults') || '1',
		children: params.get('children') || '0',
		cabin: params.get('cabin') || '经济舱',
		tripType: params.get('trip_type') || 'round',
		sort: 'priceAsc',
		priceFilter: '',
		preferences: {}
	};
	var flights = [];
	var loadingTimer = null;
	var loadingStartedAt = 0;

	var fromInput = document.getElementById('flight-from');
	var toInput = document.getElementById('flight-to');
	var departureInput = document.getElementById('flight-departure');
	var returnInput = document.getElementById('flight-return');
	var passengersInput = document.getElementById('flight-passengers');
	var flightList = document.getElementById('flight-list');
	var resultTitle = document.getElementById('result-title');
	var resultSubtitle = document.getElementById('result-subtitle');
	var summaryEl = document.getElementById('flight-summary');
	var sortSelect = document.getElementById('sort-select');
	var priceFilters = document.getElementById('price-filters');
	var searchBtn = document.getElementById('flight-search-btn');

	init();

	function init() {
		fromInput.value = state.from;
		toInput.value = state.to;
		departureInput.value = state.departure;
		returnInput.value = state.returnDate;
		passengersInput.value = buildPassengerText();
		searchBtn.addEventListener('click', refreshSearch);
		sortSelect.addEventListener('change', function () {
			state.sort = sortSelect.value;
			render();
		});
		priceFilters.addEventListener('click', function (event) {
			var button = event.target.closest('button');
			if (!button) return;
			state.priceFilter = state.priceFilter === button.dataset.price ? '' : button.dataset.price;
			Array.prototype.forEach.call(priceFilters.querySelectorAll('button'), function (btn) {
				btn.classList.toggle('active', btn.dataset.price === state.priceFilter);
			});
			render();
		});
		Array.prototype.forEach.call(document.querySelectorAll('.filter-card input[type="checkbox"]'), function (input) {
			input.addEventListener('change', function () {
				state.preferences[input.value] = input.checked;
				render();
			});
		});
		searchFlightsWithAi();
	}

	function refreshSearch() {
		state.from = fromInput.value.trim() || '北京';
		state.to = toInput.value.trim() || '上海';
		state.departure = departureInput.value.trim();
		state.returnDate = returnInput.value.trim();
		searchFlightsWithAi();
	}

	function searchFlightsWithAi() {
		flights = [];
		setLoading(true);
		renderLoading();
		fetch('/api/flight-search/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				from: state.from,
				to: state.to,
				departure: state.departure,
				return: state.returnDate,
				adults: state.adults,
				children: state.children,
				cabin: state.cabin,
				trip_type: state.tripType
			})
		}).then(function (response) {
			if (!response.ok) throw new Error('AI 查找失败：服务器返回 ' + response.status);
			return readFlightStream(response);
		}).catch(function (err) {
			flights = [];
			stopLoading();
			resultSubtitle.textContent = 'AI 机票查找失败：' + err.message;
			flightList.innerHTML = '<div class="empty-state"><i class="fa fa-warning"></i><strong>暂时没有可显示的机票</strong><span>请检查网络或 DeepSeek 配置后重试。</span></div>';
		}).finally(function () {
			setLoading(false);
		});
	}

	function readFlightStream(response) {
		var reader = response.body.getReader();
		var decoder = new TextDecoder();
		var buffer = '';
		var received = 0;

		function pump() {
			return reader.read().then(function (result) {
				if (result.done) {
					if (!received) throw new Error('AI 没有返回可用航班');
					return;
				}
				buffer += decoder.decode(result.value, { stream: true });
				var events = buffer.split('\n\n');
				buffer = events.pop();
				var streamError = null;
				events.forEach(function (eventText) {
					if (streamError) return;
					var line = eventText.split('\n').find(function (item) {
						return item.indexOf('data: ') === 0;
					});
					if (!line) return;
					try {
						var data = JSON.parse(line.substring(6));
						if (data.type === 'start') {
							resultSubtitle.textContent = data.cached ? '正在读取缓存机票结果' : 'AI 正在连接特价机票搜索';
						} else if (data.type === 'status') {
							resultSubtitle.textContent = data.content || 'AI 正在按价格生成机票';
						} else if (data.type === 'flight') {
							appendFlight(data.flight);
							received += 1;
							stopLoading();
							resultSubtitle.textContent = '已找到 ' + flights.length + ' 个航班，AI 还在继续补充';
						} else if (data.type === 'done') {
							if (!received && !flights.length) throw new Error('AI 没有返回可用航班');
							resultSubtitle.textContent = '已按价格从低到高整理 ' + flights.length + ' 个航班方案';
						} else if (data.type === 'error') {
							streamError = new Error(data.content || 'AI 查找失败');
						}
					} catch (err) {
						streamError = err;
					}
				});
				if (streamError) throw streamError;
				return pump();
			});
		}

		return pump();
	}

	function appendFlight(item) {
		var normalized = normalizeFlight(item);
		if (!normalized) return;
		var exists = flights.some(function (flight) {
			return flight.code === normalized.code;
		});
		if (exists) return;
		flights.push(normalized);
		flights.sort(function (a, b) { return a.price - b.price; });
		render();
	}

	function normalizeFlight(item) {
		if (!item || typeof item !== 'object') return null;
		return {
			airline: item.airline || '特价航班',
			code: item.code || ('TN' + Math.round(Math.random() * 9000 + 1000)),
			fromAirport: item.fromAirport || state.from + '机场',
			toAirport: item.toAirport || state.to + '机场',
			departTime: item.departTime || '08:30',
			arriveTime: item.arriveTime || '10:45',
			duration: Number(item.duration) || 135,
			direct: Boolean(item.direct),
			price: Number(item.price) || 699,
			discount: item.discount || (item.direct ? '低价直飞' : '中转特惠'),
			tags: Array.isArray(item.tags) ? item.tags.slice(0, 4) : ['特价'],
			detailUrl: normalizeUrl(item.detailUrl)
		};
	}

	function normalizeUrl(url) {
		var value = String(url || '').trim();
		if (
			/^https?:\/\//i.test(value) &&
			value.indexOf('ctrip.com/flights/') === -1 &&
			value.indexOf('flights.ctrip.com/online/list') === -1
		) return value;
		return 'https://www.bing.com/search?q=' + encodeURIComponent(state.from + ' 到 ' + state.to + ' 机票');
	}

	function setLoading(isLoading) {
		searchBtn.disabled = isLoading;
		searchBtn.innerHTML = isLoading ? '<i class="fa fa-spinner fa-spin"></i> 搜索中' : '<i class="fa fa-search"></i> 搜索';
		if (isLoading) startLoadingClock();
	}

	function startLoadingClock() {
		stopLoading();
		loadingStartedAt = Date.now();
		loadingTimer = window.setInterval(function () {
			var elapsed = Math.floor((Date.now() - loadingStartedAt) / 1000);
			if (!flights.length) resultSubtitle.textContent = 'AI 正在查找特价机票，已等待 ' + elapsed + ' 秒';
		}, 1000);
	}

	function stopLoading() {
		if (loadingTimer) {
			window.clearInterval(loadingTimer);
			loadingTimer = null;
		}
	}

	function renderLoading() {
		resultTitle.textContent = state.from + ' 到 ' + state.to + ' 特价机票';
		resultSubtitle.textContent = 'AI 正在按价格从低到高查找';
		summaryEl.innerHTML = buildSummary();
		flightList.innerHTML = [0, 1, 2].map(function () {
			return [
				'<article class="flight-card flight-card-loading">',
				'<div class="flight-main">',
				'<div class="loading-line title"></div>',
				'<div class="loading-route"></div>',
				'<div class="loading-line medium"></div>',
				'</div>',
				'<div class="flight-side"><div class="loading-line price"></div><div class="loading-button"></div></div>',
				'</article>'
			].join('');
		}).join('');
	}

	function buildPassengerText() {
		var parts = [state.adults + '成人'];
		if (Number(state.children) > 0) parts.push(state.children + '儿童');
		return parts.join(', ');
	}

	function render() {
		var list = applyFilters(flights);
		resultTitle.textContent = state.from + ' 到 ' + state.to + ' 特价机票';
		summaryEl.innerHTML = buildSummary();
		if (!list.length) {
			flightList.innerHTML = '<div class="empty-state"><i class="fa fa-plane"></i><strong>没有符合条件的航班</strong><span>可以取消部分筛选或更换日期后重新搜索。</span></div>';
			return;
		}
		flightList.innerHTML = list.map(renderFlight).join('');
	}

	function buildSummary() {
		var items = [
			['出发', state.from],
			['到达', state.to],
			['日期', state.departure || '未指定'],
			['乘客', buildPassengerText()],
			['舱位', state.cabin || '经济舱']
		];
		return items.map(function (item) {
			return '<span><b>' + escapeHtml(item[0]) + '</b>' + escapeHtml(item[1]) + '</span>';
		}).join('');
	}

	function applyFilters(source) {
		var list = source.slice();
		if (state.priceFilter) {
			var parts = state.priceFilter.split('-').map(Number);
			list = list.filter(function (flight) {
				return flight.price >= parts[0] && flight.price <= parts[1];
			});
		}
		if (state.preferences.direct) list = list.filter(function (flight) { return flight.direct; });
		if (state.preferences.early) list = list.filter(function (flight) { return Number(flight.departTime.slice(0, 2)) < 10; });
		if (state.preferences.luggage) list = list.filter(function (flight) { return flight.tags.indexOf('含手提行李') !== -1; });
		if (state.preferences.refund) list = list.filter(function (flight) { return flight.tags.indexOf('退改灵活') !== -1; });
		list.sort(function (a, b) {
			if (state.sort === 'departAsc') return a.departTime.localeCompare(b.departTime);
			if (state.sort === 'durationAsc') return a.duration - b.duration;
			return a.price - b.price;
		});
		return list;
	}

	function renderFlight(flight) {
		return [
			'<article class="flight-card">',
			'<div class="flight-main">',
			'<div class="airline-line"><div class="airline-logo">' + escapeHtml(flight.airline.slice(0, 1)) + '</div><div><h2>' + escapeHtml(flight.airline) + ' ' + escapeHtml(flight.code) + '</h2><p>' + escapeHtml(flight.discount) + '</p></div></div>',
			'<div class="route-line">',
			'<div class="time-block"><strong>' + escapeHtml(flight.departTime) + '</strong><span>' + escapeHtml(flight.fromAirport) + '</span></div>',
			'<div class="route-track"><i class="fa fa-plane"></i><span>' + formatDuration(flight.duration) + ' · ' + (flight.direct ? '直飞' : '1次中转') + '</span></div>',
			'<div class="time-block"><strong>' + escapeHtml(flight.arriveTime) + '</strong><span>' + escapeHtml(flight.toAirport) + '</span></div>',
			'</div>',
			'<div class="flight-tags">' + flight.tags.map(function (tag) { return '<span>' + escapeHtml(tag) + '</span>'; }).join('') + '</div>',
			'</div>',
			'<div class="flight-side"><div class="discount">' + escapeHtml(flight.discount) + '</div><div class="price">¥' + flight.price + '<small> 起</small></div><a class="detail-btn" href="' + escapeHtml(flight.detailUrl) + '" target="_blank" rel="noopener">查看详情</a></div>',
			'</article>'
		].join('');
	}

	function formatDuration(minutes) {
		var h = Math.floor(minutes / 60);
		var m = minutes % 60;
		return h + '小时' + (m ? m + '分' : '');
	}

	function escapeHtml(value) {
		return String(value || '')
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#039;');
	}
})();
