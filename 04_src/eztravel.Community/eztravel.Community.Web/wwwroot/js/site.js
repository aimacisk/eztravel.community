// eztravel.community — site.js

// 圖片載入失敗時,把外層 banner-card / promo-card / product-card 加 .no-image class
// 配合 site.css 的 .banner-card.no-image fallback rule,避免破圖時翠綠 on 翠綠不可讀。
(function () {
  function markBrokenImages() {
    document.querySelectorAll('img').forEach(function (img) {
      if (img.complete && img.naturalWidth === 0) {
        applyNoImage(img);
      } else {
        img.addEventListener('error', function () { applyNoImage(img); }, { once: true });
      }
    });
  }

  function applyNoImage(img) {
    var card = img.closest('.banner-card, .promo-card, .product-card, .generic-item');
    if (card) {
      card.classList.add('no-image');
      img.style.display = 'none';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markBrokenImages);
  } else {
    markBrokenImages();
  }
})();

/**
 * site.js — eztravel.community Community Module JS
 * T-eztcomm-20260602-W6PG-COMMUNITY: AJAX 視覺重建
 *
 * Features:
 *   - Star Picker interactivity (#star-picker)
 *   - Review list AJAX loader (/api/products/{id}/reviews)
 *   - Filter bar chip active state (#filter-bar)
 *   - Load-More pagination (#load-more-btn)
 *   - Review form AJAX submit (#review-composer)
 *   - Helpful button toggle (.review-card__helpful)
 *   - Rating bar chart fill (#rating-bars)
 */

(function () {
    'use strict';

    /* ─── Helpers ─── */

    function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
    function qsa(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

    /**
     * Render star HTML for a given rating (0–5, supports 0.5 increments).
     * Returns a string of 5 <span class="star star--{full|half|empty}"> elements.
     */
    function renderStars(rating) {
        var html = '';
        for (var i = 1; i <= 5; i++) {
            var cls;
            if (rating >= i) {
                cls = 'star--full';
            } else if (rating >= i - 0.5) {
                cls = 'star--half';
            } else {
                cls = 'star--empty';
            }
            html += '<span class="star ' + cls + '">★</span>';
        }
        return html;
    }

    /** Format ISO date to zh-TW locale short date. */
    function fmtDate(iso) {
        if (!iso) return '';
        try {
            return new Date(iso).toLocaleDateString('zh-TW', {
                year: 'numeric', month: '2-digit', day: '2-digit'
            });
        } catch (e) {
            return iso.slice(0, 10);
        }
    }

    /* ─── Star Picker ─── */

    function initStarPicker() {
        var picker = qs('#star-picker');
        if (!picker) return;

        var stars = qsa('.star-picker__star', picker);
        var hiddenInput = qs('#rating-input', picker.closest('form'));

        stars.forEach(function (btn, idx) {
            btn.addEventListener('mouseenter', function () {
                highlightStars(stars, idx);
            });
            btn.addEventListener('mouseleave', function () {
                var saved = hiddenInput ? parseInt(hiddenInput.value, 10) : 0;
                highlightStars(stars, saved - 1);
            });
            btn.addEventListener('click', function () {
                var rating = idx + 1;
                if (hiddenInput) hiddenInput.value = String(rating);
                highlightStars(stars, idx);
                // Persist active class
                stars.forEach(function (s, j) {
                    s.classList.toggle('is-active', j <= idx);
                });
            });
        });
    }

    function highlightStars(stars, upTo) {
        stars.forEach(function (s, j) {
            s.textContent = j <= upTo ? '★' : '☆';
        });
    }

    /* ─── Rating Distribution Bars ─── */

    function initRatingBars() {
        var container = qs('#rating-bars');
        if (!container) return;

        var productId = container.dataset.productId;
        if (!productId) return;

        fetch('/api/products/' + productId + '/reviews?page=1&pageSize=100')
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (data) {
                if (!data || !Array.isArray(data.items)) return;
                var counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
                data.items.forEach(function (rev) {
                    var r = Math.round(rev.rating);
                    if (r >= 1 && r <= 5) counts[r]++;
                });
                var total = data.items.length || 1;
                container.innerHTML = '';
                [5, 4, 3, 2, 1].forEach(function (stars) {
                    var pct = Math.round((counts[stars] / total) * 100);
                    var bar = document.createElement('div');
                    bar.className = 'rating-bar';
                    bar.innerHTML =
                        '<span class="rating-bar__label">' + stars + '</span>' +
                        '<div class="rating-bar__track">' +
                          '<div class="rating-bar__fill" style="width:' + pct + '%"></div>' +
                        '</div>' +
                        '<span class="rating-bar__count">' + counts[stars] + '</span>';
                    container.appendChild(bar);
                });
            })
            .catch(function () { /* silent — bars stay empty */ });
    }

    /* ─── Review List Loader ─── */

    var currentFilter = 'all';
    var currentPage   = 1;
    var isLoading     = false;
    var hasMore       = true;

    function buildReviewCard(rev) {
        var tmpl = qs('#review-card-template');
        if (!tmpl) return null;

        var node = tmpl.content.cloneNode(true);
        var article = qs('article', node);

        // avatar
        var avatar = qs('.review-card__avatar', article);
        if (avatar) {
            if (rev.authorAvatarUrl) {
                avatar.src = rev.authorAvatarUrl;
                avatar.alt = rev.authorName || '旅客';
            } else {
                // fallback: initial letter via CSS div style
                var div = document.createElement('div');
                div.className = 'review-card__avatar';
                div.textContent = (rev.authorName || '旅')[0];
                avatar.replaceWith(div);
            }
        }

        // name
        var nameEl = qs('.review-card__name', article);
        if (nameEl) nameEl.textContent = rev.authorName || '匿名旅客';

        // date
        var dateEl = qs('.review-card__date', article);
        if (dateEl) dateEl.textContent = fmtDate(rev.createdAt);

        // rating
        var ratingEl = qs('.review-card__rating', article);
        if (ratingEl) {
            ratingEl.innerHTML = renderStars(rev.rating);
            ratingEl.className = 'review-card__rating star-rating';
        }

        // text
        var textEl = qs('.review-card__text', article);
        if (textEl) textEl.textContent = rev.text || '';

        // photos
        var photosEl = qs('.review-card__photos', article);
        if (photosEl && Array.isArray(rev.photoUrls) && rev.photoUrls.length) {
            rev.photoUrls.forEach(function (url) {
                var img = document.createElement('img');
                img.src = url;
                img.alt = '評論照片';
                img.className = 'review-card__photo';
                photosEl.appendChild(img);
            });
        }

        // helpful button
        var helpfulBtn = qs('.review-card__helpful', article);
        if (helpfulBtn) {
            var countSpan = qs('.helpful-count', helpfulBtn);
            if (countSpan) countSpan.textContent = String(rev.helpfulCount || 0);
            helpfulBtn.dataset.reviewId = rev.id;
            helpfulBtn.addEventListener('click', function () {
                onHelpfulClick(helpfulBtn);
            });
        }

        return article;
    }

    function loadReviews(productId, page, filter, append) {
        var list = qs('#review-list');
        var btn  = qs('#load-more-btn');
        if (!list || isLoading) return;

        isLoading = true;
        if (btn) btn.disabled = true;

        var url = '/api/products/' + productId + '/reviews?page=' + page + '&pageSize=10';
        if (filter && filter !== 'all') url += '&ratingFilter=' + encodeURIComponent(filter);

        fetch(url)
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (data) {
                isLoading = false;
                if (!data) return;

                if (!append) list.innerHTML = '';

                var items = data.items || [];
                if (items.length === 0 && !append) {
                    var li = document.createElement('li');
                    li.className = 'review-section__empty';
                    li.textContent = '尚無評論，成為第一個分享旅遊體驗的人！';
                    list.appendChild(li);
                }

                items.forEach(function (rev) {
                    var card = buildReviewCard(rev);
                    if (card) {
                        var li = document.createElement('li');
                        li.appendChild(card);
                        list.appendChild(li);
                    }
                });

                hasMore = data.hasNextPage === true;
                if (btn) {
                    btn.disabled = !hasMore;
                    btn.textContent = hasMore ? '載入更多評論' : '已顯示全部評論';
                }
            })
            .catch(function () {
                isLoading = false;
                if (btn) btn.disabled = false;
            });
    }

    function initReviewList() {
        var list = qs('#review-list');
        if (!list) return;

        var productId = list.dataset.productId;
        if (!productId) return;

        currentPage = 1;
        loadReviews(productId, 1, 'all', false);

        // Load More button
        var btn = qs('#load-more-btn');
        if (btn) {
            btn.addEventListener('click', function () {
                if (isLoading || !hasMore) return;
                currentPage++;
                loadReviews(productId, currentPage, currentFilter, true);
            });
        }
    }

    /* ─── Filter Bar ─── */

    function initFilterBar() {
        var bar = qs('#filter-bar');
        if (!bar) return;

        var list      = qs('#review-list');
        var productId = list ? list.dataset.productId : null;

        qsa('.filter-bar__chip', bar).forEach(function (chip) {
            chip.addEventListener('click', function () {
                qsa('.filter-bar__chip', bar).forEach(function (c) {
                    c.classList.remove('is-active');
                });
                chip.classList.add('is-active');
                currentFilter = chip.dataset.filter || 'all';
                currentPage   = 1;
                if (productId) loadReviews(productId, 1, currentFilter, false);
            });
        });

        // Activate "全部" chip by default
        var allChip = qs('[data-filter="all"]', bar);
        if (allChip) allChip.classList.add('is-active');
    }

    /* ─── Helpful Button ─── */

    function onHelpfulClick(btn) {
        if (btn.classList.contains('is-voted')) return; // already voted

        var reviewId = btn.dataset.reviewId;
        if (!reviewId) return;

        fetch('/api/reviews/' + reviewId + '/helpful', { method: 'POST' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (data) {
                btn.classList.add('is-voted');
                var countSpan = qs('.helpful-count', btn);
                if (countSpan && data && data.helpfulCount != null) {
                    countSpan.textContent = String(data.helpfulCount);
                } else if (countSpan) {
                    countSpan.textContent = String(parseInt(countSpan.textContent, 10) + 1);
                }
            })
            .catch(function () { /* silent */ });
    }

    /* ─── Review Form Submit ─── */

    function initReviewForm() {
        var form = qs('#review-composer');
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var productId = form.dataset.productId;
            if (!productId) return;

            var rating   = parseInt(qs('#rating-input', form).value, 10);
            var textarea = qs('textarea[name="text"]', form);
            var text     = textarea ? textarea.value.trim() : '';

            var feedback = qs('#review-feedback', form);

            if (!rating || rating < 1) {
                showFeedback(feedback, '請選擇評分星等', false);
                return;
            }
            if (text.length < 10) {
                showFeedback(feedback, '留言至少需要 10 個字', false);
                return;
            }

            var submitBtn = qs('.review-composer__submit', form);
            if (submitBtn) submitBtn.disabled = true;

            fetch('/api/products/' + productId + '/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating: rating, text: text })
            })
                .then(function (r) {
                    if (r.ok || r.status === 201) return r.json();
                    return r.json().then(function (err) { throw err; });
                })
                .then(function () {
                    showFeedback(feedback, '評論送出成功，感謝您的分享！', true);
                    form.reset();
                    highlightStars(qsa('.star-picker__star', form), -1);
                    // Reload list to show new review at top
                    var list = qs('#review-list');
                    if (list && list.dataset.productId) {
                        currentPage = 1;
                        loadReviews(list.dataset.productId, 1, currentFilter, false);
                    }
                })
                .catch(function (err) {
                    var msg = (err && err.message) ? err.message : '送出失敗，請稍後再試';
                    showFeedback(feedback, msg, false);
                })
                .finally(function () {
                    if (submitBtn) submitBtn.disabled = false;
                });
        });
    }

    function showFeedback(el, message, isSuccess) {
        if (!el) return;
        el.textContent = message;
        el.className   = 'review-composer__feedback ' + (isSuccess ? 'is-success' : 'is-error');
        el.style.display = '';
        setTimeout(function () {
            if (isSuccess) el.className = 'review-composer__feedback';
        }, 5000);
    }

    /* ─── Init ─── */

    function init() {
        initStarPicker();
        initRatingBars();
        initReviewList();
        initFilterBar();
        initReviewForm();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

}());
