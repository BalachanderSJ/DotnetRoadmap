# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Part A, Day 6 — Trees and BST"},
        {"t": "p", "text": "Outcome. You can walk a binary tree in pre-order, in-order, and post-order, compute depth without confusing it with a shortest-path claim, and explain lowest common ancestor for a BST and for a general binary tree. You know a BST is O(height), and height can be n."},
        {"t": "p", "text": "Time box. About 3.5 hours. Draw a seven-node tree and write the three visit orders by hand. Code in-order and both depth methods. Code both LCA methods. The variant is validating a BST with an explicit range, using long bounds so Int32.MinValue has a home."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "A binary tree node has a value, a left child, and a right child, either of which may be null. Pre-order visits the node, then the left subtree, then the right. In-order visits left, node, right. On a binary search tree, in-order yields the values in sorted order, which is the check you use when you are unsure the tree is a BST. Post-order visits both subtrees before the node, which is the order you want when the node depends on the children, as depth does."},
        {"t": "p", "text": "Depth here means the number of nodes on the longest path from the root to a leaf. An empty tree has depth 0. A single node has depth 1. Ask which convention they want if they say height, because some people count edges and a single node is then 0. The recursive form is one plus the larger child. The same recursion on a skewed tree is one frame per node. A chain of tens of thousands of nodes can throw StackOverflowException. An explicit queue computes the same number level by level and keeps the frames off the call stack. That is the form you switch to when the tree is untrusted."},
        {"t": "p", "text": "A BST keeps smaller values on the left and larger values on the right. Search and insert are O(height). A balanced tree gives you log n. A tree built from sorted inserts is a linked list, and the cost is n. You say that before you promise log n."},
        {"t": "p", "text": "Lowest common ancestor in a BST: walk from the root. If both targets are smaller, go left. If both are larger, go right. Otherwise this node is the split, and it is the ancestor. This assumes both values are in the tree. If one is missing, the walk can still return a node, and it is the wrong answer. Ask."},
        {"t": "p", "text": "Lowest common ancestor in a general binary tree: search both sides. If a node is one of the targets, or is null, return it. If the left search and the right search both return a node, this node is the ancestor. If only one side returns a node, pass that node up. This also assumes both targets are present. If one is missing, the method returns the one it found."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public sealed class TreeNode
{
    public int Value;
    public TreeNode? Left;
    public TreeNode? Right;
    public TreeNode(int value) => Value = value;
}

public static void InOrder(TreeNode? node, List<int> output)
{
    if (node is null)
        return;
    InOrder(node.Left, output);
    output.Add(node.Value);
    InOrder(node.Right, output);
}

public static int MaxDepth(TreeNode? node)
{
    if (node is null)
        return 0;
    return 1 + Math.Max(MaxDepth(node.Left), MaxDepth(node.Right));
}

public static int MaxDepthIterative(TreeNode? root)
{
    if (root is null)
        return 0;

    var queue = new Queue<TreeNode>();
    queue.Enqueue(root);
    int depth = 0;
    while (queue.Count > 0)
    {
        int width = queue.Count;
        for (int i = 0; i < width; i++)
        {
            TreeNode node = queue.Dequeue();
            if (node.Left is not null)
                queue.Enqueue(node.Left);
            if (node.Right is not null)
                queue.Enqueue(node.Right);
        }
        depth++;
    }
    return depth;
}

public static TreeNode? LcaBst(TreeNode? node, int a, int b)
{
    while (node is not null)
    {
        if (a < node.Value && b < node.Value)
            node = node.Left;
        else if (a > node.Value && b > node.Value)
            node = node.Right;
        else
            return node;
    }
    return null;
}

public static TreeNode? Lca(TreeNode? node, TreeNode p, TreeNode q)
{
    if (node is null || ReferenceEquals(node, p) || ReferenceEquals(node, q))
        return node;

    TreeNode? left = Lca(node.Left, p, q);
    TreeNode? right = Lca(node.Right, p, q);
    if (left is not null && right is not null)
        return node;
    return left ?? right;
}"""},
        {"t": "p", "text": "Build the tree 4 with left 2 and right 6, and 2 with left 1 and right 3. In-order is 1, 2, 3, 4, 6. Depth is 3. LcaBst of 1 and 3 is the node 2. LcaBst of 1 and 6 is the node 4, because the targets are on different sides. The iterative depth captures the queue count before the loop that drains that level. If you measure Count inside the loop, newly enqueued children stretch the level and the depth is wrong."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "A full traversal is O(n) time and O(height) call-stack memory, or O(width) queue memory for the level-order form. BST search is O(height). LCA on a BST is O(height) time and O(1) extra memory in the loop above. LCA on a general tree is O(n) time in the form that searches the whole tree, and O(height) stack. You can stop early once both targets are found. The simple form is the one you write unless they ask for the pruning."},
        {"t": "warn", "title": "Interview trap", "text": "Promising log n on a BST you did not balance. Using value equality for LCA when the tree can hold duplicates or when they handed you node identities. Capturing the queue count after you have already enqueued children. Recursing a skewed tree of untrusted size. Forgetting to ask whether both nodes exist. An int range check that cannot represent a bound outside Int32 for the validation variant."},
        {"t": "lead", "title": "Say this", "text": "In-order on a BST is sorted. Depth is one plus the deeper child, and I switch to a queue when the tree can be a chain. BST cost is the height. LCA in a BST walks to the split. LCA in a general tree is the node where the two searches meet, and I ask whether both nodes are present."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write InOrder, MaxDepthIterative, and LcaBst from memory. Say the visit order of your seven-node drawing before you run anything.",
            "Variant: IsBst. Pass a long lower bound and a long upper bound. A node is valid when its value is strictly inside the range. The left child inherits the node's value as its upper bound.",
            "Call it as IsBst(root, long.MinValue, long.MaxValue). State what you do if duplicates are allowed. The version below rejects duplicates.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static bool IsBst(TreeNode? node, long lo, long hi)
{
    if (node is null)
        return true;
    if (node.Value <= lo || node.Value >= hi)
        return false;
    return IsBst(node.Left, lo, node.Value)
        && IsBst(node.Right, node.Value, hi);
}"""},
        {"t": "p", "text": "Checking only that left is smaller than the node misses a left grandchild that is larger than the root. The range carries the ancestors. Time O(n). The long bounds are the overflow-shaped pitfall: an int bound cannot sit strictly outside every int."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 7 — Heaps and PriorityQueue"},
        {"t": "p", "text": "Outcome. You can take the top K frequent numbers with PriorityQueue, and you can explain merging K sorted lists as the same heap with one current head per list. You know the BCL queue is a min-heap."},
        {"t": "p", "text": "Time box. About 3.5 hours. Code top K until the size-K rule is automatic. Then code the merge from the sketch without looking. The variant is the Kth largest element, which is top K with a single answer. Leave 20 minutes to say what Dequeue removes."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "PriorityQueue<TElement, TPriority> is a binary heap. With the default comparer it dequeues the smallest priority first. It is not a max-heap, it is not SortedSet, and it allows two elements with the same priority. SortedSet rejects a duplicate priority unless you invent a tie-break, which is why people reach for it and then lose equal frequencies. Dequeue returns the element. TryDequeue can also hand back the priority."},
        {"t": "p", "text": "Top K frequent: count in a dictionary, then keep a min-heap of size K ordered by frequency. For each distinct value, enqueue it with its frequency. When the heap grows past K, dequeue. You just threw away the smallest frequency in the heap, so the heap holds the K largest frequencies seen so far. At the end, dequeue the survivors. Their order is smallest frequency first. If the caller wants them sorted, sort the K items, which is cheap because K is small. If K is larger than the number of distinct values, you return all of them."},
        {"t": "p", "text": "Equal frequencies have no stable winner. The heap does not remember input order. If the problem requires a tie-break, put a sequence number in the priority. A tuple (frequency, sequence) uses the default tuple comparer, item by item. You decide which sequence should lose when the heap trims, and you say it. If any tied value is acceptable, you leave the priority as the frequency."},
        {"t": "p", "text": "Merge K sorted lists uses the same heap. Each list contributes its current head. The priority is the head value, so the smallest head comes out first. You append it, and if that list has a next element you enqueue the next index. You never insert a whole list. The heap size is at most K. A full concatenation followed by a sort is correct and does more work when the lists are already sorted. Say the worse one, then the heap."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static int[] TopKFrequent(int[] nums, int k)
{
    if (k <= 0)
        return Array.Empty<int>();

    var counts = new Dictionary<int, int>();
    foreach (int n in nums)
        counts[n] = counts.GetValueOrDefault(n) + 1;

    // Min-heap of at most k values, priority = frequency.
    var heap = new PriorityQueue<int, int>();
    foreach (var (value, freq) in counts)
    {
        heap.Enqueue(value, freq);
        if (heap.Count > k)
            heap.Dequeue();
    }

    var result = new int[heap.Count];
    for (int i = result.Length - 1; i >= 0; i--)
        result[i] = heap.Dequeue();
    return result;
}

public static int[] MergeSorted(IReadOnlyList<int[]> lists)
{
    var heap = new PriorityQueue<(int list, int index), int>();
    for (int i = 0; i < lists.Count; i++)
    {
        if (lists[i].Length > 0)
            heap.Enqueue((i, 0), lists[i][0]);
    }

    var result = new List<int>();
    while (heap.TryDequeue(out var current, out _))
    {
        result.Add(lists[current.list][current.index]);
        int next = current.index + 1;
        if (next < lists[current.list].Length)
            heap.Enqueue((current.list, next), lists[current.list][next]);
    }
    return result.ToArray();
}"""},
        {"t": "p", "text": "Trace top K on [1, 1, 1, 2, 2, 3] with K = 2. Counts are 1 thrice, 2 twice, 3 once. The heap keeps 1 and 2, and 3 is dequeued when the size hits 3. Filling the result from the end puts the larger frequency first. The problem often accepts any order of the K values. Say that."},
        {"t": "p", "text": "MergeSorted on [1, 4, 5], [1, 3, 4], and [2, 6] yields 1, 1, 2, 3, 4, 4, 5, 6. Empty lists are skipped, so they do not enqueue a fake head. Two equal heads are both valid. The heap may emit either first."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Counting is O(n). The heap never holds more than K + 1 items, so the count phase of top K is O(d log K) for d distinct values, which is O(n log K) at worst. Memory is O(d) for the map plus O(K) for the heap. Merge is O(N log K) time for N total elements and O(K) heap memory, plus O(N) for the output. Sorting the concatenation is O(N log N). You pick the heap when K is smaller than N, which is the point of the question."},
        {"t": "warn", "title": "Interview trap", "text": "Treating PriorityQueue as a max-heap and keeping the wrong K. Using SortedSet and dropping a second item with the same frequency. Forgetting to skip an empty list, then reading index 0. Claiming the merge is O(N log N) after you have already written the heap. Assuming dequeue order is stable across equal priorities."},
        {"t": "lead", "title": "Say this", "text": "PriorityQueue dequeues the smallest priority. For top K I keep a heap of size K and throw away the smallest frequency. Merge K sorted lists is one current head per list in that same heap, N log K, and I skip empty lists. Ties are unordered unless I put a sequence number in the priority."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write TopKFrequent from memory, including k <= 0 and the case k greater than the number of distinct values.",
            "Variant: Kth largest element in an unsorted array. Keep a min-heap of size K of the values themselves. The root is the Kth largest. Do not sort the array unless you are stating the simpler O(n log n) answer first.",
            "Say what the root is after the loop, in one sentence.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static int KthLargest(int[] nums, int k)
{
    var heap = new PriorityQueue<int, int>();
    foreach (int n in nums)
    {
        heap.Enqueue(n, n);
        if (heap.Count > k)
            heap.Dequeue();
    }
    return heap.Peek();
}"""},
        {"t": "p", "text": "Peek returns the smallest of the K largest, which is the Kth largest, without removing it. This assumes k is between 1 and nums.Length. Ask before you index off the end. Time O(n log K), extra memory O(K)."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 8 — Graphs"},
        {"t": "p", "text": "Outcome. You can build an adjacency list, run BFS and DFS, and detect a cycle in a directed graph. You can say how the undirected case differs."},
        {"t": "p", "text": "Time box. About 3.5 hours. Build the list from an edge array on paper, then in code. Write the directed cycle DFS with three colors and be able to point at a back edge. Write Kahn's algorithm as the second cycle test. The variant is an undirected cycle, which must ignore the edge back to the parent."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "For nodes numbered 0 through n - 1, an adjacency list is an array of lists. A sparse id space uses Dictionary<int, List<int>> and a HashSet for seen nodes. You build the list once. A matrix is the wrong default unless the graph is tiny and dense, because the matrix is n squared memory and the interview graphs are sparse."},
        {"t": "p", "text": "BFS from Day 3 gives you distance on an unweighted graph. DFS gives you reachability and the cycle test. For a directed cycle, color each node unseen, on-stack, or done. A neighbor that is still on the stack is a back edge, and that is a cycle. A neighbor that is done is a cross edge or a forward edge into finished work, and it is not a new cycle. You must run the search from every unseen node, or a cycle in a later component survives."},
        {"t": "p", "text": "Kahn's algorithm is the same fact as a queue. Compute indegree. Enqueue every node with indegree 0. Pop a node, append it to the order, and decrement its neighbors. A neighbor that hits 0 is enqueued. If the order contains every node, you have a topological order. If it does not, some nodes still have incoming edges inside a cycle. The short order is the cycle report. BFS here is not a shortest path. It is a drain of the graph."},
        {"t": "p", "text": "An undirected cycle is a different predicate. The edge back to the parent is how you arrived, and it is not a cycle. A neighbor that is already seen and is not the parent is a cycle. A self-loop is a cycle. Do not paste the directed coloring onto an undirected graph and then treat the parent as a back edge. You will report a cycle on every tree."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static bool HasDirectedCycle(int n, List<(int From, int To)> edges)
{
    var adj = new List<int>[n];
    for (int i = 0; i < n; i++)
        adj[i] = new List<int>();
    foreach (var (from, to) in edges)
        adj[from].Add(to);

    const int Unseen = 0;
    const int OnStack = 1;
    const int Done = 2;
    var color = new int[n];

    for (int i = 0; i < n; i++)
    {
        if (color[i] == Unseen && DfsCycle(i, adj, color))
            return true;
    }
    return false;
}

static bool DfsCycle(int node, List<int>[] adj, int[] color)
{
    const int OnStack = 1;
    const int Done = 2;
    color[node] = OnStack;
    foreach (int next in adj[node])
    {
        if (color[next] == OnStack)
            return true;
        if (color[next] == 0 && DfsCycle(next, adj, color))
            return true;
    }
    color[node] = Done;
    return false;
}

public static List<int> TopologicalOrder(int n, List<(int From, int To)> edges)
{
    var adj = new List<int>[n];
    var indegree = new int[n];
    for (int i = 0; i < n; i++)
        adj[i] = new List<int>();
    foreach (var (from, to) in edges)
    {
        adj[from].Add(to);
        indegree[to]++;
    }

    var queue = new Queue<int>();
    for (int i = 0; i < n; i++)
    {
        if (indegree[i] == 0)
            queue.Enqueue(i);
    }

    var order = new List<int>(n);
    while (queue.Count > 0)
    {
        int node = queue.Dequeue();
        order.Add(node);
        foreach (int next in adj[node])
        {
            indegree[next]--;
            if (indegree[next] == 0)
                queue.Enqueue(next);
        }
    }
    return order.Count == n ? order : new List<int>();
}"""},
        {"t": "p", "text": "Edges (0, 1), (1, 2), (2, 1) are a directed cycle. DFS colors 1 as on-stack, reaches 2, and from 2 sees 1 still on the stack. Kahn enqueues 0, then never drains 1 and 2, so the order is short and the method returns an empty list. Returning empty is a choice. You can return the partial order and let the caller compare the count. Say which one you did. A caller who forgets to check the count will schedule a cyclic graph."},
        {"t": "p", "text": "The recursive DFS has the same depth limit as any other recursion. A long chain is a deep stack. If the node count can be large, say you would move the DFS onto an explicit stack and keep the color array. Do not discover that at the end of a 40-minute slot if the constraint says a hundred thousand nodes."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Building the list is O(n + e). Directed DFS is O(n + e) time and O(n) memory for the colors, plus O(height) call stack. Kahn is O(n + e) time and O(n) memory for the queue and the indegree array. A missing node id past n - 1 is an input error. Ask whether node ids are dense before you allocate the array."},
        {"t": "warn", "title": "Interview trap", "text": "Reporting a directed cycle when you see any seen node, including a finished one, which flags a diamond as a cycle. Forgetting to start DFS from every component. Treating a short topological order as a successful schedule. Using DFS distance as a shortest path. On an undirected graph, counting the parent edge as a cycle. A dictionary adjacency list with graph[node] when the node has no list."},
        {"t": "lead", "title": "Say this", "text": "I build an adjacency list. BFS for unweighted distance, DFS for reachability. A directed cycle is a back edge to a node still on the stack, or a topological order that does not include everyone. An undirected cycle ignores the edge back to the parent. I start the search from every node."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write HasDirectedCycle from memory and trace a three-node cycle and a diamond that is not a cycle.",
            "Variant: undirected cycle. The adjacency list stores both directions. DFS takes the parent index. Skip the parent. A seen neighbor that is not the parent is a cycle.",
            "Say the time cost in n and e, not just n.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static bool HasUndirectedCycle(int n, List<(int A, int B)> edges)
{
    var adj = new List<int>[n];
    for (int i = 0; i < n; i++)
        adj[i] = new List<int>();
    foreach (var (a, b) in edges)
    {
        adj[a].Add(b);
        adj[b].Add(a);
    }

    var seen = new bool[n];
    for (int i = 0; i < n; i++)
    {
        if (!seen[i] && DfsUndirected(i, -1, adj, seen))
            return true;
    }
    return false;
}

static bool DfsUndirected(int node, int parent, List<int>[] adj, bool[] seen)
{
    seen[node] = true;
    foreach (int next in adj[node])
    {
        if (next == parent)
            continue;
        if (seen[next] || DfsUndirected(next, node, adj, seen))
            return true;
    }
    return false;
}"""},
        {"t": "p", "text": "Parent -1 is the start, and no real node has that id in a 0-based graph. A self-loop has next == node, which is seen and is not the parent, so it returns true. Time O(n + e)."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 9 — Recursion and backtracking"},
        {"t": "p", "text": "Outcome. You can generate subsets by choosing and undoing, and you can explain permutations as the same search with a used set. You copy the path when you record an answer."},
        {"t": "p", "text": "Time box. About 3.5 hours. Write subsets until the undo is muscle memory. Trace the call tree for three numbers on paper, including the copy. Then write the permutation variant. Spend the last 20 minutes on when this recursion is safe and when a different recursion is a stack overflow."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "Backtracking is a depth-first search over decisions. For subsets, the decisions are in index order: take this element, or skip it, and never look backward, so you do not emit the same subset in two orders. You record a copy of the current path at each node, including the empty path at the start. Then you add the element, recurse from the next index, and remove the element. The remove is the backtrack. Without it, every later subset inherits the earlier choice."},
        {"t": "p", "text": "The path is one list you mutate. If you add that list into the result, every slot in the result points at the same list, and at the end every slot is empty, because you undid every add. The copy is new List<int>(path). That allocation is the output, and it is required."},
        {"t": "p", "text": "Permutations use the same undo with a different branch. At each depth you try every unused element, mark it used, recurse, and unmark it. The depth is n, and the branching is n, then n - 1, then n - 2. You record a copy only when the path length is n. Subsets record at every node. Do not mix those two lines."},
        {"t": "p", "text": "The call depth of subsets or permutations is n, and n is small because the output is already 2^n or n!. The recursion that overflows in C# is the one that follows a chain: a skewed tree, a linked list, a graph path of tens of thousands. Tail calls are not a feature you can rely on. If a backtracking constraint says n can be 100, the issue is time, not the stack. If a different problem says the list can be 100,000 long, you stop recursing."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static List<List<int>> Subsets(int[] nums)
{
    var result = new List<List<int>>();
    var path = new List<int>();
    Walk(0);
    return result;

    void Walk(int start)
    {
        result.Add(new List<int>(path));
        for (int i = start; i < nums.Length; i++)
        {
            path.Add(nums[i]);
            Walk(i + 1);
            path.RemoveAt(path.Count - 1);
        }
    }
}"""},
        {"t": "p", "text": "Trace [1, 2]. The first record is the empty list. Take 1, record [1]. Take 2, record [1, 2]. Undo 2, undo 1. Take 2 from the start index, record [2]. Undo 2. The result has four lists, and they are four different objects. Start at i + 1 so 2 is never followed by 1. That is what keeps [1, 2] and [2, 1] from both appearing. If the problem wants permutations, that restriction is wrong. If the input has duplicates and the problem wants unique subsets, sort first and skip a duplicate element at the same depth. Ask before you write that skip."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "There are 2^n subsets. Recording each costs time proportional to its length, so the total time is O(n 2^n). Memory is the output plus O(n) for the path and the call stack. Permutations are O(n * n!) time for the same reason: n! leaves, each copied at size n. You say the output size out loud so an exponential answer sounds like a choice and not like a mistake. If they need one subset that matches a constraint, you stop at the first match and the worst case is still exponential."},
        {"t": "warn", "title": "Interview trap", "text": "Adding the path list by reference, so every result mutates together. Forgetting the undo. Starting the next loop at i instead of i + 1 and either looping forever or emitting duplicates, depending on the rest of the code. Recursing on start and also on start + 1 without a structure, and emitting each subset many times. Treating this depth-n search as unsafe, and treating a recursive walk of a 100,000-node chain as safe. The second one is the stack overflow."},
        {"t": "lead", "title": "Say this", "text": "I choose or skip in index order, I copy the path when I record it, and I undo the choice on the way back. Subsets are n times 2 to the n. Permutations are the same undo with a used set, and I copy only at depth n. I recurse here because n is small. I do not recurse down a chain that can be huge."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write Subsets from memory. Trace [1, 2] and confirm four distinct lists.",
            "Variant: permutations of distinct integers. Use a bool array for used, or a HashSet if you prefer. Copy the path only when its count equals n.",
            "Say the complexity before you run it, and run it on three elements so you expect six results.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static List<List<int>> Permutations(int[] nums)
{
    var result = new List<List<int>>();
    var path = new List<int>(nums.Length);
    var used = new bool[nums.Length];
    Walk();
    return result;

    void Walk()
    {
        if (path.Count == nums.Length)
        {
            result.Add(new List<int>(path));
            return;
        }

        for (int i = 0; i < nums.Length; i++)
        {
            if (used[i])
                continue;
            used[i] = true;
            path.Add(nums[i]);
            Walk();
            path.RemoveAt(path.Count - 1);
            used[i] = false;
        }
    }
}"""},
        {"t": "p", "text": "The bool array is the used set. A HashSet<int> of indices is the same idea and allocates more. Time O(n * n!), stack depth n."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 10 — Dynamic programming starter, and how to talk through a question"},
        {"t": "p", "text": "Outcome. You can write climbing stairs with two running totals, and coin change as a one-dimensional table, including the case with no solution. You can talk through a coding question in a fixed order: clarify, brute force, complexity, code, test. You can say why greedy fails on coin change."},
        {"t": "p", "text": "Time box. About 3.5 hours. Spend 40 minutes on the two DP methods and the greedy counterexample. Spend 40 minutes rewriting them from memory. Spend 30 minutes on the house-robber variant. Spend the remaining time on the talk-through, out loud, using two-sum as the script, then once more using coin change. The talk-through is the page you are allowed to use in every later interview, including the ones that are not DP."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "A starter dynamic program is a brute-force recursion you can see repeating itself, rewritten so each smaller input is solved once. If you can define dp[i] as the answer for a smaller prefix or a smaller amount, and you can say the transition in one sentence, you have the starter. Two dimensions can wait. You begin with the recursion even if you never ship it, because the table is that recursion with the calls removed."},
        {"t": "p", "text": "Climbing stairs: you may take 1 or 2 steps, and you want the number of ways to reach n. To reach i you came from i - 1 or from i - 2, so ways(i) = ways(i - 1) + ways(i - 2). That is Fibonacci, with ways(1) = 1 and ways(2) = 2. The recursive tree recomputes the same i many times and is exponential, and a deep n is also a stack overflow. You keep two running totals and walk up to n. Time O(n), extra memory O(1)."},
        {"t": "p", "text": "The totals leave Int32 in the mid-40s of the Fibonacci sequence. If n can be that large, the total is a long. The usual interview n is small. Use a long anyway if you do not want to think about the boundary while you are writing the loop."},
        {"t": "p", "text": "Coin change: the fewest coins that sum to the amount, unlimited supply of each coin. dp[a] is the fewest coins that make amount a. dp[0] is 0. Every other cell starts as a sentinel meaning impossible. For each amount, you try each coin that fits, and you take one plus the answer for the remainder. If a cell is still the sentinel at the end, return -1. A coin of 0 or less does not belong in the loop. Greedy, taking the largest coin first, is wrong for some sets. Coins 1, 3, and 4, amount 6: greedy takes 4 + 1 + 1, three coins. The table takes 3 + 3, two coins. You mention that so they do not hear you say DP when greedy would do, and you do not hear yourself say greedy on this problem."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static long ClimbStairs(int n)
{
    if (n <= 2)
        return n;

    long prev2 = 1;
    long prev1 = 2;
    for (int i = 3; i <= n; i++)
    {
        long current = prev1 + prev2;
        prev2 = prev1;
        prev1 = current;
    }
    return prev1;
}

public static int CoinChange(int[] coins, int amount)
{
    if (amount < 0)
        return -1;
    if (amount == 0)
        return 0;

    var dp = new int[amount + 1];
    Array.Fill(dp, amount + 1);
    dp[0] = 0;

    for (int a = 1; a <= amount; a++)
    {
        foreach (int coin in coins)
        {
            if (coin <= 0)
                throw new ArgumentOutOfRangeException(nameof(coins));
            if (coin <= a)
                dp[a] = Math.Min(dp[a], dp[a - coin] + 1);
        }
    }

    return dp[amount] > amount ? -1 : dp[amount];
}"""},
        {"t": "p", "text": "ClimbStairs(4) is 5: 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2. CoinChange of coins [1, 3, 4] and amount 6 is 2. CoinChange of [2] and amount 3 is -1, because 3 stays at the sentinel. The sentinel amount + 1 is larger than any real answer, since you cannot need more coins than the amount when a coin of 1 exists, and when it does not exist the sentinel simply survives. dp[a - coin] + 1 can be the sentinel plus one, which is still larger than any real answer and loses the Math.Min. That is fine."},
        {"t": "p", "text": "Throwing on a non-positive coin is a guard, not the algorithm. If you would rather return -1, say so. An infinite loop from a zero coin is the bug the guard prevents."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Climbing stairs is O(n) time and O(1) extra memory. The naive recursion is exponential time and O(n) stack. Coin change is O(amount * coins) time and O(amount) memory. You can talk about the recursion with a cache as O(amount * coins) too. The table is that cache, written in order so each remainder is already filled. This order works because the recurrence only looks at smaller amounts."},
        {"t": "warn", "title": "Interview trap", "text": "Writing the recursive Fibonacci and calling it dynamic programming. Using greedy on coin change. An int total that wraps. A zero coin. Forgetting the impossible case and returning the sentinel as if it were a real count. Building a two-dimensional table when one dimension of amount is the whole state."},
        {"t": "lead", "title": "Say this", "text": "Climbing stairs is Fibonacci. I keep two running totals in a long, because the recursive tree repeats work and the int total overflows. Coin change is a table of the fewest coins for each smaller amount, and I return -1 when the amount stays unreachable. Greedy is wrong for coins 1, 3, and 4 with amount 6."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write both methods from memory. Compute climbing stairs for n = 4 by hand and coin change for [1, 3, 4] and 6 by hand.",
            "Variant: house robber. A row of house values, you cannot rob two adjacent houses. dp at each house is the max of skipping it or taking it plus the answer two houses back. Keep two running totals, the same shape as climbing stairs.",
            "Say the transition before you write the loop.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static int Rob(int[] houses)
{
    int skipPrev = 0;
    int takePrev = 0;
    foreach (int money in houses)
    {
        int skip = Math.Max(skipPrev, takePrev);
        int take = skipPrev + money;
        skipPrev = skip;
        takePrev = take;
    }
    return Math.Max(skipPrev, takePrev);
}"""},
        {"t": "p", "text": "skip is the best answer for the houses before this one. take is this house plus the best answer that did not include the previous house. Time O(n), extra memory O(1). An int is enough while the sum fits. If the problem says the values can be large, use a long. The adjacent constraint is why this is not a plain sum of the positive houses."},

        {"t": "h2", "text": "How I talk through a coding question"},
        {"t": "p", "text": "This is the other half of Day 10, and it is the script for every coding screen, not only for dynamic programming. You talk in this order even when you already see the answer. The interviewer is scoring the order."},
        {"t": "b", "numbered": True, "items": [
            "Clarify. Restate the input, the output, and the question in one sentence. Ask about empty input, duplicates, negative numbers, overflow, and whether you need the original index. Ask for a bound on n if they have one. Agree on a small example, including the answer.",
            "Brute force. Say the obvious loops and their cost. Do not apologize. A correct n-squared answer that you can finish is worth more than a silent search for the optimal one. Ask whether n-squared is acceptable before you leave it.",
            "Better structure. Name the pattern and why the brute force was doing repeated work: a map for a complement, two pointers for a sorted pair, a queue for a shortest unweighted path, a table for a recurrence that repeats.",
            "Complexity. Time and extra memory, including the output when the output is the memory. Say expected when a hash map is involved. Say the height when a tree is involved.",
            "Code. Name the variables for what they mean. Handle the empty input first. Leave the C# pitfall in the code, not in a comment you forget: TryGetValue, a long sum, a half-open bound, a copied list.",
            "Test. Walk the example. Then the empty input, a single element, a duplicate, and the case that fails if the pitfall is present. If a test fails, say what the invariant was and fix that, rather than nudging a bound until the sample passes.",
        ]},
        {"t": "h3", "text": "The script, spoken on two-sum"},
        {"t": "code", "text": """Clarify.
  I return two indices that add to the target, or an empty array.
  I am assuming one answer exists in the sample, the same element
  cannot be used twice, and the numbers fit in an int.
  Example: [2, 7, 11, 15], target 9, indices 0 and 1.

Brute force.
  Every pair, n squared time, constant extra memory.
  I can write that if n is a few thousand. I am assuming n can be larger.

Better.
  One pass. Map from value to index. For each value, look up target - value.
  Store the index after the lookup so a value is not paired with itself.

Complexity.
  Expected linear time, linear memory.

Code.
  Dictionary, TryGetValue, return the earlier index then this one.

Test.
  The sample.
  [3, 3], target 6, indices 0 and 1.
  A single element, empty result.
  If they allow values near Int32 boundaries, the complement moves to a long."""},
        {"t": "p", "text": "Then you stop talking and type. If you get stuck, you say which step you are on. Stuck in the code is not a reason to abandon the tests. Stuck in the optimal structure is a reason to write the brute force and then improve one loop."},
        {"t": "h3", "text": "The same script, one paragraph, on coin change"},
        {"t": "p", "text": "Clarify: fewest coins to make the amount, unlimited counts, -1 if it is impossible, coins are positive. Brute force: try every coin and recurse on the remainder, which repeats the same remainder. Better: dp[a] is the fewest coins for a, filled from 0 to amount. Complexity: amount times the number of coins, and a table of size amount + 1. Test: amount 0 returns 0, coins [1, 3, 4] and amount 6 returns 2, coins [2] and amount 3 returns -1. Greedy is the wrong improvement. Then code."},
        {"t": "lead", "title": "Say this", "text": "I clarify the empty case and the overflow, I say the brute force and its cost, I name the structure that removes the repeated work, and I test the sample plus the case that breaks. If I cannot see the optimal answer yet, I write the brute force and improve it. I do not go quiet."},
        {"t": "h2", "text": "What you can skip"},
        {"t": "p", "text": "You can skip segment trees, heavy-light decomposition, and contest tricks that exist to shave a log factor off an already acceptable solution. You cannot skip the ten shapes above. A tech-lead screen uses them as a way to watch you code in C# under a clock: collections, bounds, and whether you test. The system-design half of this guide starts next. It assumes you can still say, in one minute, how you would attack a small coding question if they drop one into the whiteboard."},
        {"t": "break"},
    ]
