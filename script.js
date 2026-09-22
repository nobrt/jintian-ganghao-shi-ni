const progress = document.querySelector('.progress span');
const audio = document.querySelector('#ambient');
const soundButton = document.querySelector('.sound-toggle');

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
}, { threshold: 0.14 });
document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));

// 照片素材存在时自动显示；未放入素材时保留胶片感占位画面。
document.querySelectorAll('[data-image]').forEach((frame) => {
  const source = frame.dataset.image;
  const image = new Image();
  image.onload = () => {
    const placeholder = frame.querySelector('.photo-placeholder');
    placeholder.style.backgroundImage = `url("${source}")`;
    placeholder.style.backgroundSize = 'cover';
    placeholder.style.backgroundPosition = 'center';
    placeholder.querySelector('span').textContent = '';
    frame.classList.add('has-photo');
  };
  image.src = source;
});

function updateScrollEffects() {
  const max = document.documentElement.scrollHeight - innerHeight;
  progress.style.width = `${max ? (scrollY / max) * 100 : 0}%`;
  document.querySelectorAll('.frame').forEach((frame) => {
    const box = frame.getBoundingClientRect();
    const offset = (box.top - innerHeight / 2) * -0.025;
    frame.style.transform = `translateY(${offset}px)`;
  });
}
addEventListener('scroll', updateScrollEffects, { passive: true });
updateScrollEffects();

addEventListener('pointermove', (event) => {
  document.documentElement.style.setProperty('--mouse-x', `${event.clientX}px`);
  document.documentElement.style.setProperty('--mouse-y', `${event.clientY}px`);
}, { passive: true });

soundButton.addEventListener('click', async () => {
  try {
    if (audio.paused) {
      await audio.play();
      soundButton.setAttribute('aria-pressed', 'true');
      soundButton.querySelector('.sound-label').textContent = 'SOUND ON';
    } else {
      audio.pause();
      soundButton.setAttribute('aria-pressed', 'false');
      soundButton.querySelector('.sound-label').textContent = 'SOUND OFF';
    }
  } catch {
    soundButton.querySelector('.sound-label').textContent = 'ADD AUDIO FILE';
  }
});

document.querySelector('.replay').addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
