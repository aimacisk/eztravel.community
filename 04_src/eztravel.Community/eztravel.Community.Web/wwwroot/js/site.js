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
