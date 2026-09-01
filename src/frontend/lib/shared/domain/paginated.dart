/// A page of list results. `nextPage == null` means the last page.
class Paginated<T> {
  const Paginated({
    required this.items,
    this.page = 1,
    this.nextPage,
    this.total,
  });

  const Paginated.single(this.items)
      : page = 1,
        nextPage = null,
        total = null;

  final List<T> items;
  final int page;
  final int? nextPage;
  final int? total;

  bool get hasMore => nextPage != null;

  Paginated<R> map<R>(R Function(T) f) => Paginated(
        items: items.map(f).toList(),
        page: page,
        nextPage: nextPage,
        total: total,
      );

  Paginated<T> append(Paginated<T> next) => Paginated(
        items: [...items, ...next.items],
        page: next.page,
        nextPage: next.nextPage,
        total: next.total,
      );
}
