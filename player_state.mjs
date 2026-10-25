/** Derive rehearsal position from audio time, never CPU or wall-clock time. */
export class RehearsalState {
  constructor(model, events) {
    this.model = model;
    this.events = events;
    this.reset();
  }

  reset() {
    this.auto = true;
    this.page = 0;
    this.fired = new Set();
    this.highBeat = -Infinity;
    this.lastTime = -1;
    this.processed = 0;
  }

  manual(delta) {
    this.auto = false;
    this.page = Math.max(0, Math.min(this.model.pages.length - 1, this.page + delta));
  }

  at(time) {
    if (time < this.lastTime) {
      const auto = this.auto;
      this.reset();
      this.auto = auto;
    }
    this.lastTime = time;
    let lo = 0, hi = this.events.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (this.events[mid].time <= time) lo = mid + 1;
      else hi = mid;
    }
    const beat = lo ? this.events[lo - 1].beat : this.model.measures[0].start;

    // Consume every crossed event even when browser animation frames are delayed.
    for (let i = this.processed; i < lo; i++) {
      this.highBeat = Math.max(this.highBeat, this.events[i].beat);
      this.model.boundaries.forEach((boundary, index) => {
        if (this.highBeat >= boundary - 2) this.fired.add(index);
      });
    }
    this.processed = lo;
    if (this.auto) {
      this.page = this.model.boundaries.filter(boundary => this.highBeat >= boundary).length;
    }
    const last = this.model.measures.at(-1);
    const measure = this.model.measures.find(m => m.start <= beat && beat < m.end)
      ?? (beat >= last.end ? last : null);
    const preview = this.auto && this.fired.has(this.page)
      && this.highBeat < this.model.boundaries[this.page] ? this.page + 1 : null;
    return {page: this.page, measure, preview, beat};
  }
}
