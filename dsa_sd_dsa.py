# -*- coding: utf-8 -*-

def blocks():
    return [
        {"t": "h1", "text": "Part A — DSA in C# for the coding screen"},
        {"t": "p", "text": "Ten days, one pattern a day. The code is the code you write in a console app, not pseudocode. Assume the usings you already know: System, System.Collections.Generic, and System.Linq. Each drill is two problems: the worked example from memory, then the variant. Close this page before you type."},

        {"t": "h1", "text": "Part A, Day 1 — Arrays, strings, and hash maps"},
        {"t": "p", "text": "Outcome. You can solve a frequency problem, an anagram problem, and a two-sum problem in one pass, and you can say what the dictionary costs. You can also say when a sort is the wrong tool because it is unstable or because it throws the original index away."},
        {"t": "p", "text": "Time box. About 3.5 hours. Spend 30 minutes tracing the three methods on paper. Spend 45 minutes rewriting them from memory. Spend 30 minutes on complexity and the two pitfalls, missing keys and overflow. Spend 45 minutes on the variant. Spend the rest comparing, then speaking the Say this box in under 90 seconds."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "An array gives you O(1) indexing and no fast membership test. A Dictionary or a HashSet turns a membership or a frequency question into expected O(1) per element, at the cost of extra memory and a worst case you do not pretend is impossible. You reach for the map when the question is: have I seen this value, how many times, or what index had the complement."},
        {"t": "p", "text": "Two-sum is the shape. For each number, the complement is target minus that number. If the complement is already in the map, you have the pair and the earlier index. If not, you store this number and its index. One pass, expected linear time, linear memory. The brute force pair of loops is n squared and is what you say first so they hear you can start."},
        {"t": "p", "text": "Anagrams are a frequency problem. Two strings are anagrams when they have the same length and the same character counts. A group of anagrams shares a key. If the problem promises lowercase English letters, a count of 26 is the key. The counts need a delimiter when you join them into a string, because 1 followed by 11 is the same text as 11 followed by 1. If the alphabet is open, sort the characters and use the sorted string as the key. Sorting characters does not care about sort stability. Stability matters later, when equal business keys must keep their input order."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static int[] TwoSum(int[] nums, int target)
{
    var seen = new Dictionary<int, int>(nums.Length);
    for (int i = 0; i < nums.Length; i++)
    {
        int need = target - nums[i];
        if (seen.TryGetValue(need, out int j))
            return new[] { j, i };
        seen[nums[i]] = i;
    }
    return Array.Empty<int>();
}

public static bool AreAnagrams(string left, string right)
{
    if (left.Length != right.Length)
        return false;

    var counts = new Dictionary<char, int>();
    foreach (char c in left)
        counts[c] = counts.GetValueOrDefault(c) + 1;

    foreach (char c in right)
    {
        if (!counts.TryGetValue(c, out int n) || n == 0)
            return false;
        counts[c] = n - 1;
    }
    return true;
}

// Assumption for this key: the word is lowercase a-z.
public static List<List<string>> GroupAnagrams(string[] words)
{
    var groups = new Dictionary<string, List<string>>();
    foreach (string word in words)
    {
        string key = AnagramKey(word);
        if (!groups.TryGetValue(key, out var list))
        {
            list = new List<string>();
            groups[key] = list;
        }
        list.Add(word);
    }
    return groups.Values.ToList();
}

static string AnagramKey(string word)
{
    Span<int> counts = stackalloc int[26];
    foreach (char c in word)
        counts[c - 'a']++;

    var sb = new StringBuilder(26 * 4);
    for (int i = 0; i < counts.Length; i++)
    {
        sb.Append(counts[i]);
        sb.Append('#');
    }
    return sb.ToString();
}"""},
        {"t": "p", "text": "Trace two-sum on [2, 7, 11, 15] with target 9. At 2 the map is empty, so you store 2 at index 0. At 7 the complement is 2, which is in the map, so the answer is indices 0 and 1. You store a value after the lookup, so a value is not paired with itself unless it appears twice."},
        {"t": "p", "text": "Span is doing a small job here: the 26 counts live on the stack, so you do not allocate an array per word. The string key is still an allocation, and that is fine. If the interviewer wants less allocation and the groups are small, say so and keep the clear version. Do not start the interview inside stackalloc."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Two-sum is expected O(n) time and O(n) extra memory. Anagram compare is O(n) time and O(alphabet) memory. Grouping m words of length k with a 26-count key is O(m k) time. The sort-the-characters key is O(m k log k) and is the right key when the alphabet is not a fixed 26. Hashing is expected constant time per operation. You say expected, because a pathological hash is a conversation you will not pretend you have closed."},
        {"t": "h2", "text": "The sort you did not use"},
        {"t": "p", "text": "You can sort pairs of (value, index) and walk inward. That is O(n log n) and it keeps the index because the index rides inside the tuple. It is a worse two-sum, and it is a useful backup if you blank on the map. Array.Sort on those tuples is not stable, and you do not care, because the index is part of the value. The day stability matters is a list of orders sorted by priority where two orders share a priority and the original order is the tie-break. Array.Sort and List<T>.Sort may reorder those equals. Enumerable.OrderBy is stable. Say that if they ask you to sort."},
        {"t": "p", "text": "target - nums[i] is an int subtraction. In the default unchecked context it wraps. The usual interview input fits. If the problem says values can sit at the ends of the int range, compute the complement in a long and say why."},
        {"t": "warn", "title": "Interview trap", "text": "dict[c]++ throws when c is missing. GetValueOrDefault or TryGetValue is the fix. A second trap is using the sorted position as if it were the original index. A third is an anagram key with no delimiter between counts. A fourth is calling two strings anagrams after sorting them with a culture-sensitive compare. For a machine key, ordinal is the compare you want."},
        {"t": "lead", "title": "Say this", "text": "One pass, a dictionary of value to index, TryGetValue so a miss is not an exception. Expected linear time and linear memory. I hash the raw character counts when the alphabet is fixed, and I only sort when I need a key for an open alphabet or when I need order. If equal keys must keep their input order, I use OrderBy because Array.Sort is not stable."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Close the page. Write TwoSum and AreAnagrams from memory, including the empty return and the length check.",
            "Variant: first non-repeating character. One pass to count, a second pass to return the first character whose count is 1. Return a nullable char when there is none.",
            "State time, memory, and the missing-key pitfall before you look back.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static char? FirstUnique(string s)
{
    var counts = new Dictionary<char, int>();
    foreach (char c in s)
        counts[c] = counts.GetValueOrDefault(c) + 1;

    foreach (char c in s)
    {
        if (counts[c] == 1)
            return c;
    }
    return null;
}"""},
        {"t": "p", "text": "The second loop may use counts[c] because every character was inserted in the first loop. That is the difference between a key you know exists and a key you hope exists. Time O(n), memory O(alphabet)."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 2 — Two pointers and sliding window"},
        {"t": "p", "text": "Outcome. You can move two indices toward each other on a palindrome or a sorted pair, and you can grow and shrink a window over a contiguous range. You compute the length as right - left + 1 without hesitating."},
        {"t": "p", "text": "Time box. About 3.5 hours. Trace both methods on a short string and a short array. Rewrite them from memory. Then do the fixed-window variant. Leave 20 minutes to say the invariant out loud: what the window contains after each move of left."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "Two pointers apply when you can decide, from the values at the ends, which end to move. A palindrome compares ends and walks inward. A sorted array looking for a pair with a given sum moves the left end up when the sum is too small and the right end down when the sum is too large. You do not use two pointers on an unsorted array and then claim the pair is found, unless you sorted a copy first and paid n log n."},
        {"t": "p", "text": "A sliding window applies when the answer is a contiguous subarray or substring, and growing the right end only adds information you can undo by moving the left end. The window is valid, or it is not, and you always know which. For a longest substring without a repeated character, the window contains unique characters. When the next character is already inside, you shrink from the left until it is not. For a minimum length subarray whose sum reaches a target, the numbers need to be non-negative so that growing the right end only increases the sum and shrinking the left end only decreases it. Negative numbers break that monotone move, and you say so instead of forcing the pattern."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static bool IsPalindrome(ReadOnlySpan<char> s)
{
    int i = 0;
    int j = s.Length - 1;
    while (i < j)
    {
        while (i < j && !char.IsLetterOrDigit(s[i]))
            i++;
        while (i < j && !char.IsLetterOrDigit(s[j]))
            j--;
        if (char.ToLowerInvariant(s[i]) != char.ToLowerInvariant(s[j]))
            return false;
        i++;
        j--;
    }
    return true;
}

public static int LongestUnique(string s)
{
    var inWindow = new HashSet<char>();
    int left = 0;
    int best = 0;
    for (int right = 0; right < s.Length; right++)
    {
        while (!inWindow.Add(s[right]))
        {
            inWindow.Remove(s[left]);
            left++;
        }
        int length = right - left + 1;
        if (length > best)
            best = length;
    }
    return best;
}

public static int MinSubarrayLen(int[] nums, int target)
{
    int left = 0;
    long sum = 0;
    int best = int.MaxValue;
    for (int right = 0; right < nums.Length; right++)
    {
        sum += nums[right];
        while (sum >= target && left <= right)
        {
            int length = right - left + 1;
            if (length < best)
                best = length;
            sum -= nums[left];
            left++;
        }
    }
    return best == int.MaxValue ? 0 : best;
}"""},
        {"t": "p", "text": "ReadOnlySpan<char> lets the palindrome walk the string without building a cleaned copy. Indexing a span is the same as indexing the string. This is a justified use of Span: it removes an allocation without hiding the algorithm. A string is UTF-16, so s[i] is a code unit, not a grapheme. For the usual interview alphabet that is enough, and you mention it if they hand you emoji or combining marks."},
        {"t": "p", "text": "Trace LongestUnique on abcabcbb. The window grows to abc. At the second a, Add fails, you remove from the left until a is gone, and the window becomes bca. The best length is 3. HashSet.Add returns false when the character was already present, which is the test and the insert in one call."},
        {"t": "p", "text": "MinSubarrayLen keeps the sum in a long. An int sum of a large array wraps in the unchecked context and the window then shrinks or grows for the wrong reason. The problem statement for this pattern assumes non-negative numbers. Say that assumption before you code."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "The palindrome is O(n) time and O(1) extra memory. LongestUnique is O(n) time because each index enters and leaves the window at most once, and O(alphabet) memory. MinSubarrayLen is O(n) time and O(1) extra memory on non-negative numbers. A window that shrinks from the inside, or a sum that is allowed to go backwards because of negatives, is no longer this pattern."},
        {"t": "warn", "title": "Interview trap", "text": "The length is right - left + 1, not right - left. The inner while on the palindrome must also keep i < j, or you walk off the string. Moving only the right pointer and restarting left at zero on every duplicate is still correct and no longer linear. An int running sum is the overflow. Two pointers on unsorted data is a guess."},
        {"t": "lead", "title": "Say this", "text": "Ends move inward when a comparison tells me which end is wrong. A window grows on the right and shrinks on the left while I can state what the window means. Length is right minus left plus one. I keep the sum in a long, and I only use this window when adding on the right moves the sum in one direction."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write IsPalindrome and LongestUnique from memory.",
            "Variant: maximum sum of a fixed window of size k. One pass, add the new element, subtract the element that fell out, track the best sum in a long.",
            "Say what you return for an empty array and for k larger than the array.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static long MaxSumFixed(int[] nums, int k)
{
    if (k <= 0 || k > nums.Length)
        return 0;

    long sum = 0;
    for (int i = 0; i < k; i++)
        sum += nums[i];

    long best = sum;
    for (int right = k; right < nums.Length; right++)
    {
        sum += nums[right];
        sum -= nums[right - k];
        if (sum > best)
            best = sum;
    }
    return best;
}"""},
        {"t": "p", "text": "Fixed windows do not need a left pointer if you can name the element that left: it is at right - k. Time O(n), extra memory O(1). Returning 0 for a bad k is a choice; in the interview, ask what they want for k = 0."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 3 — Stack and queue"},
        {"t": "p", "text": "Outcome. You can match brackets with a stack, explain a monotonic stack on the next-greater problem, and use a queue for breadth-first search so the first visit is the shortest path in an unweighted graph."},
        {"t": "p", "text": "Time box. About 3.5 hours. Code the brackets until the leftover-open case and the early-close case are both tests you remember. Then the next-greater loop. Then a tiny graph BFS. The variant is the daily-temperatures form of the same monotonic stack."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "A stack is last in, first out. It remembers the thing you opened most recently, which is exactly what nested brackets need. You push opens. On a close, the stack must be non-empty and the pop must be the matching open. At the end the stack must be empty. ([)] fails because the close does not match the latest open, even though the counts of each bracket would match."},
        {"t": "p", "text": "A monotonic stack keeps indices whose values are still waiting for an answer, in order. For the next greater element you keep a stack of indices whose values are decreasing. When the new value is greater than the value at the top, that top has found its answer, you pop it, and you keep popping while the new value is still greater. Each index is pushed once and popped once."},
        {"t": "p", "text": "A queue is first in, first out. Breadth-first search uses it. You mark a node seen when you enqueue it, not when you dequeue it, or the same neighbor gets enqueued many times. In an unweighted graph the first time you reach a node is a shortest path. Depth-first search finds a path. It does not find the shortest one. Use System.Collections.Generic.Stack<T> and Queue<T>. The non-generic Stack and Queue are the old untyped collections."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static bool IsValidBrackets(string s)
{
    var stack = new Stack<char>();
    foreach (char c in s)
    {
        if (c is '(' or '[' or '{')
        {
            stack.Push(c);
            continue;
        }

        if (stack.Count == 0)
            return false;

        char open = stack.Pop();
        bool match = (open, c) is ('(', ')') or ('[', ']') or ('{', '}');
        if (!match)
            return false;
    }
    return stack.Count == 0;
}

public static int[] NextGreater(int[] nums)
{
    var result = new int[nums.Length];
    Array.Fill(result, -1);
    var stack = new Stack<int>();
    for (int i = 0; i < nums.Length; i++)
    {
        while (stack.Count > 0 && nums[stack.Peek()] < nums[i])
            result[stack.Pop()] = nums[i];
        stack.Push(i);
    }
    return result;
}

public static int ShortestPath(Dictionary<int, List<int>> graph, int start, int goal)
{
    var queue = new Queue<int>();
    var dist = new Dictionary<int, int> { [start] = 0 };
    queue.Enqueue(start);

    while (queue.Count > 0)
    {
        int node = queue.Dequeue();
        if (node == goal)
            return dist[node];

        if (!graph.TryGetValue(node, out var nexts))
            continue;

        foreach (int next in nexts)
        {
            if (dist.ContainsKey(next))
                continue;
            dist[next] = dist[node] + 1;
            queue.Enqueue(next);
        }
    }
    return -1;
}"""},
        {"t": "p", "text": "Trace brackets on ([)]. Push '(', push '[', then ')' does not match '[', so the method returns false. Trace ()[] : each close matches the latest open, and the stack ends empty. Trace (( : the loop ends with two opens still on the stack, so the method returns false."},
        {"t": "p", "text": "NextGreater on [2, 1, 2, 4, 3] yields [4, 2, 4, -1, -1]. The strict < means an equal neighbor is not a greater element. If the problem wants the next greater or equal, you change the comparison and you say you changed it. The stack stores indices, not values, so you can write the answer back into the right slot."},
        {"t": "p", "text": "ShortestPath marks distance at enqueue time, which is also the seen mark. TryGetValue covers a node that has no outgoing list, so a missing key is a dead end and not an exception. The distance is the edge count. This graph is unweighted. A weighted graph wants a priority queue, which is Day 7's tool, and you do not pretend BFS still gives the shortest path once edges have costs."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Brackets are O(n) time and O(n) stack memory. Next greater is O(n) time because each index is pushed and popped at most once, and O(n) memory. BFS is O(n + e) time for n nodes and e edges, and O(n) memory for the queue and the distance map. Building the adjacency list is part of the cost. Say it."},
        {"t": "warn", "title": "Interview trap", "text": "A count of opens and closes accepts ([)]. Forgetting the final empty-stack check accepts ((. Using a stack for BFS changes the visit order and loses the shortest-path claim. Marking a node seen on dequeue lets the queue hold the same node many times. dict[node] on a node with no edge list throws."},
        {"t": "lead", "title": "Say this", "text": "A stack matches the latest open. A monotonic stack of indices answers the next greater element in one pass, each index pushed once. A queue is breadth-first, and in an unweighted graph the first visit is the shortest path. I mark the node when I enqueue it."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write IsValidBrackets and NextGreater from memory. Include the tests (), ([)], and ((.",
            "Variant: daily temperatures. Given an array of temperatures, return how many days until a warmer day, or 0. Same decreasing stack of indices. The answer is i - poppedIndex, not the temperature.",
            "Say why the stack stores the index.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static int[] DaysUntilWarmer(int[] temps)
{
    var wait = new int[temps.Length];
    var stack = new Stack<int>();
    for (int i = 0; i < temps.Length; i++)
    {
        while (stack.Count > 0 && temps[stack.Peek()] < temps[i])
        {
            int earlier = stack.Pop();
            wait[earlier] = i - earlier;
        }
        stack.Push(i);
    }
    return wait;
}"""},
        {"t": "p", "text": "The array starts as zeros, so an index that never pops stays 0. Time O(n), memory O(n)."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 4 — Linked lists"},
        {"t": "p", "text": "Outcome. You can reverse a singly linked list without losing the tail, and you can detect a cycle by reference identity. You know why the node type is a class."},
        {"t": "p", "text": "Time box. About 3.5 hours. Draw a four-node list and rewire it with a pencil before you code. Then write reverse from memory until you can do it without the drawing. Then Floyd. The variant is the start of the cycle. Leave time to explain the record trap out loud."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "The interview list is a node type you control, with a value and a Next reference. LinkedList<T> in the BCL is a doubly linked list with a different API. You can mention it. You do not use it to answer reverse, because the point of the question is the rewiring."},
        {"t": "p", "text": "Reverse walks once. You keep three references: previous, current, and the old next. You must copy current.Next into a local before you overwrite it, or the rest of the list is gone. Then you point current.Next at previous, advance previous to current, and advance current to the saved next. When current is null, previous is the new head. The empty list and the single-node list both fall out of the same loop."},
        {"t": "p", "text": "A cycle means a node's Next eventually points at an earlier node. Floyd uses two pointers, slow moving one step and fast moving two. If there is no cycle, fast reaches the end. If there is a cycle, fast laps slow and they meet. You compare references, not values. Two nodes can hold the same integer and not be a cycle."},
        {"t": "p", "text": "Make the node a sealed class. A record compares by value. If you write slow == fast on a record, equality walks the chain, which is the wrong question and can blow the stack on a cycle. ReferenceEquals asks the question you meant. A recursive reverse is easy to write and uses one stack frame per node. A long list can throw StackOverflowException. C# does not promise it will turn that recursion into a loop. The iterative reverse is the one you ship in the interview."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public sealed class ListNode
{
    public int Value;
    public ListNode? Next;
    public ListNode(int value) => Value = value;
}

public static ListNode? Reverse(ListNode? head)
{
    ListNode? previous = null;
    ListNode? current = head;
    while (current is not null)
    {
        ListNode? next = current.Next;
        current.Next = previous;
        previous = current;
        current = next;
    }
    return previous;
}

public static bool HasCycle(ListNode? head)
{
    ListNode? slow = head;
    ListNode? fast = head;
    while (fast?.Next is not null)
    {
        slow = slow!.Next;
        fast = fast.Next.Next;
        if (ReferenceEquals(slow, fast))
            return true;
    }
    return false;
}"""},
        {"t": "p", "text": "Trace 1 -> 2 -> 3. Start with previous null and current 1. Save 2, point 1 at null, previous becomes 1, current becomes 2. Save 3, point 2 at 1, previous becomes 2, current becomes 3. Save null, point 3 at 2, previous becomes 3, current becomes null. Return 3, which now points at 2, which points at 1, which points at null."},
        {"t": "p", "text": "The ! on slow is there because the compiler does not connect the loop condition on fast to slow. On a well-formed list slow is non-null whenever fast.Next is non-null. If you would rather avoid the operator, assign slow to a local and return false when it is null. That branch does not run for a real list."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Reverse is O(n) time and O(1) extra memory. Cycle detection is O(n) time and O(1) extra memory. A HashSet of seen nodes is also correct, and it uses O(n) memory. Give Floyd when they ask for constant memory. Give the set when you want the simpler code and memory is free. Say which one you wrote."},
        {"t": "warn", "title": "Interview trap", "text": "Overwriting Next before saving it loses the list. Comparing Value finds duplicate numbers, not a cycle. A record with == walks values. A recursive reverse on a long list is a stack overflow. Forgetting to return previous returns null, because current ends null. The BCL LinkedList<T> is not the answer they asked for."},
        {"t": "lead", "title": "Say this", "text": "I keep the old Next in a local, then point the node at previous. The new head is previous when current runs off the end. A cycle is two pointers and ReferenceEquals, on a class, in constant extra memory. A HashSet of nodes is the linear-memory version. I do not recurse down a list that can be long."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write the node class, Reverse, and HasCycle from memory. Draw the four pointers on a four-node list after each iteration.",
            "Variant: return the node where the cycle begins, or null when there is no cycle. After slow and fast meet, walk one pointer from the head and one from the meeting point, one step at a time. They meet at the start.",
            "State the memory of Floyd versus the memory of a seen set.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static ListNode? CycleStart(ListNode? head)
{
    ListNode? slow = head;
    ListNode? fast = head;
    while (fast?.Next is not null)
    {
        slow = slow!.Next;
        fast = fast.Next.Next;
        if (!ReferenceEquals(slow, fast))
            continue;

        ListNode? fromHead = head;
        while (!ReferenceEquals(fromHead, slow))
        {
            fromHead = fromHead!.Next;
            slow = slow!.Next;
        }
        return fromHead;
    }
    return null;
}"""},
        {"t": "p", "text": "You can state the meeting rule without deriving the algebra in the interview. If they ask why it works: the meeting point is some number of steps into the cycle, and walking from the head covers the prefix in the same number of steps the pointer inside the cycle needs to finish a lap back to the start. Time O(n), extra memory O(1)."},
        {"t": "break"},

        {"t": "h1", "text": "Part A, Day 5 — Binary search"},
        {"t": "p", "text": "Outcome. You can write a binary search with a half-open range that terminates, and you can binary-search the answer when the array is not what you are indexing. You can say the feasibility predicate in one sentence."},
        {"t": "p", "text": "Time box. About 3.5 hours. Write the lower-bound loop until the invariant is boring. Then the ship-capacity problem, which is the answer-range form. The variant is the upper bound, the first index whose value is strictly greater than the target. Spend the last half hour on off-by-one: change one bound the wrong way and watch the loop stick, so you remember why you will not mix the two loop styles."},
        {"t": "h2", "text": "The idea"},
        {"t": "p", "text": "Binary search needs a monotone predicate. On a sorted array the predicate is: this index is too far left, or it is a candidate. The version you should be able to write half asleep uses a half-open interval [lo, hi). lo starts at 0. hi starts at a.Length, not a.Length - 1, because the insertion point might be past the last element. While lo is less than hi, the midpoint is lo + (hi - lo) / 2. Integer division makes that midpoint strictly below hi, so the range shrinks. If a[mid] is less than the target, the answer is in (mid, hi), so lo becomes mid + 1. Otherwise the answer is in [lo, mid], so hi becomes mid. When the loop ends, lo is the first index whose value is greater than or equal to the target, or a.Length if every value is smaller."},
        {"t": "p", "text": "lo + (hi - lo) / 2 avoids the overflow of (lo + hi) / 2. Two large indices can sum past Int32.MaxValue. Array lengths can be large enough for that sum to wrap. The wrapped midpoint is nonsense, and the loop can run forever or throw. This is the overflow pitfall in its interview form."},
        {"t": "p", "text": "Array.BinarySearch exists. It returns the index, or the bitwise complement of the insertion point when the value is missing. You may mention it. You still write the loop, because they want the invariant, and because the complement trick is easy to get wrong under pressure."},
        {"t": "p", "text": "Searching on the answer is the same loop with a different predicate. The classic form here is: what is the smallest truck capacity that ships every package, in order, within D days. Capacity is monotone. If a capacity works, every larger capacity works. If it fails, every smaller capacity fails. lo is the heaviest single package, because a package cannot be split. hi is the sum of the packages, which ships in one day. You binary-search that range. The predicate walks the array once and counts the days. The array is not sorted. The search space is."},
        {"t": "h2", "text": "Worked example"},
        {"t": "code", "text": """public static int LowerBound(int[] a, int target)
{
    int lo = 0;
    int hi = a.Length; // half-open [lo, hi)
    while (lo < hi)
    {
        int mid = lo + ((hi - lo) / 2);
        if (a[mid] < target)
            lo = mid + 1;
        else
            hi = mid;
    }
    return lo;
}

public static int MinShipCapacity(int[] weights, int maxDays)
{
    long lo = 0;
    long hi = 0;
    foreach (int weight in weights)
    {
        if (weight > lo)
            lo = weight;
        hi += weight;
    }

    while (lo < hi)
    {
        long mid = lo + ((hi - lo) / 2);
        if (CanShip(weights, maxDays, mid))
            hi = mid;
        else
            lo = mid + 1;
    }
    return checked((int)lo);
}

static bool CanShip(int[] weights, int maxDays, long capacity)
{
    int days = 1;
    long load = 0;
    foreach (int weight in weights)
    {
        if (load + weight > capacity)
        {
            days++;
            load = 0;
            if (days > maxDays)
                return false;
        }
        load += weight;
    }
    return true;
}"""},
        {"t": "p", "text": "LowerBound on [1, 2, 2, 4] for target 2 returns 1, the first 2. For target 3 it returns 3, the index of 4, which is the insertion point. For target 9 it returns 4, the length. That last answer is why hi starts at the length."},
        {"t": "p", "text": "CanShip assumes every weight fits in the capacity. The search maintains that, because lo starts at the max weight. The sum of weights is a long, so a large array does not wrap hi. checked((int)lo) is a loud failure if a caller ever asked this method to return a capacity past Int32.MaxValue. In the interview you can return long instead and skip the cast. Say which one you chose."},
        {"t": "h2", "text": "Complexity"},
        {"t": "p", "text": "Lower bound is O(log n) comparisons and O(1) extra memory, after the array is sorted. If you sorted it yourself, add the n log n. MinShipCapacity does O(log S) feasibility checks, where S is the sum of the weights, and each check is O(n). Total O(n log S) time and O(1) extra memory. You do not say log n for the answer-range form. The n is inside the predicate."},
        {"t": "warn", "title": "Interview trap", "text": "Mixing while (lo <= hi) with hi = mid can stick forever when lo and hi differ by one, because mid becomes lo and nothing moves. Pick the half-open form and stay with it. (lo + hi) / 2 overflows. Forgetting that lo must be at least the heaviest package makes CanShip spin, because a package larger than the capacity never fits. Off-by-one on the day counter usually comes from resetting the load and also forgetting to count the last open day, or from counting an extra day at the end."},
        {"t": "lead", "title": "Say this", "text": "Half-open range, midpoint is lo plus half the gap, and the predicate is monotone. On a sorted array that finds the first index at or after the target. On an answer range I binary-search the capacity, and the array walk is only the check. I keep the sum in a long."},
        {"t": "h2", "text": "Drill"},
        {"t": "b", "numbered": True, "items": [
            "Write LowerBound from memory. Trace target 2, target 3, and a target past the end on [1, 2, 2, 4].",
            "Variant: UpperBound, the first index whose value is strictly greater than the target. Change the comparison to <= and keep the same bounds.",
            "Then write MinShipCapacity once, and say the predicate in one sentence before you write CanShip.",
        ]},
        {"t": "h3", "text": "Variant, after you have written it"},
        {"t": "code", "text": """public static int UpperBound(int[] a, int target)
{
    int lo = 0;
    int hi = a.Length;
    while (lo < hi)
    {
        int mid = lo + ((hi - lo) / 2);
        if (a[mid] <= target)
            lo = mid + 1;
        else
            hi = mid;
    }
    return lo;
}"""},
        {"t": "p", "text": "On [1, 2, 2, 4] with target 2, UpperBound returns 3. LowerBound returned 1. The gap between them is the run of equals. Time is still O(log n)."},
        {"t": "break"},
    ]
