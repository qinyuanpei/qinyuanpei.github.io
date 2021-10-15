---
toc: true
title: 一道 HashSet 面试题引发的蝴蝶效应
categories:
  - 编程语言
tags:
  - HashSet
  - 编程
  - 面试
  - 源码
copyright: true
abbrlink: 3411909634
date: 2020-10-20 12:19:02
---
没错，我又借着“面试题”的名头来搞事情了，今天要说的是 HashSet ，而这确实是一个实际面试中遇到的问题。当时的场景大概是这样的，面试官在了解了你的知识广度以后，决心来考察一番你的基本功底，抛出了一个看起来平平无奇的问题：说一说你平时工作中都用到了哪些数据结构。你心想，这还不简单，`Array`、`ArrayList`、`List`、`Dictionary`、`HashSet`、`Stack`、`Queue`...等等各种集合类简直如数家珍，甚至你还能说出这些数据结构间的优劣以及各自使用的场景。可没想到，面试官话锋一转，直接来一句，“你能说说 HashSet 去重的原理吗”，好家伙，你这简直不按套路出牌啊...本着每次面试都有一点收获的初心，于是就有了今天这篇博客，不同的是，顺着这个思路继续深挖下去，博主又发现了几个平时关注不到的技术盲点，所以，博主称之为：一道 HashSet 面试题引发的蝴蝶效应。

# HashSet源代码解读

OK，首先，我们来回答第一个问题，即：**HashSet 去重的原理是什么？**。为此，博主翻阅了 HashSet 的 [源代码](https://referencesource.microsoft.com/#System.Core/System/Collections/Generic/HashSet.cs,1044)。首先，我们会注意到 HashSet 的构造函数，它需要一个类型为`IEqualityComparer<T>`的参数。从这个命名上我们就可以知道，这是一个用于相等性比较的接口，我们初步推测，HashSet 去重应该和这个接口有关：

```CSharp
    public HashSet()
        : this(EqualityComparer<T>.Default) { }
 
    public HashSet(int capacity)
        : this(capacity, EqualityComparer<T>.Default) { }
 
    public HashSet(IEqualityComparer<T> comparer) { }
 
    public HashSet(IEnumerable<T> collection)
        : this(collection, EqualityComparer<T>.Default) { }

    public HashSet(IEnumerable<T> collection, IEqualityComparer<T> comparer)
        : this(comparer) { }
```
我们都知道 HashSet 可以去重，比如，我们向 HashSet 添加多个相同的元素，实际上 HashSet 中最终只会有一个元素。所以，我们自然而然地想到，看看 HashSet 中的 `Add()` 方法呗，或许能从这里看出一点端倪。HashSet 中一共有两个 `Add()` 方法，它们内部都调用了 `AddIfNotPresent()` 方法：
```CSharp
void ICollection<T>.Add(T item) {
    AddIfNotPresent(item);
}

 public bool Add(T item) {
    return AddIfNotPresent(item);
}
```
继续循着蛛丝马迹一路 F12 ，我们来看看这个方法的具体实现：
```CSharp
private bool AddIfNotPresent(T value) {
    if (m_buckets == null) {
        Initialize(0);
    }
 
    int hashCode = InternalGetHashCode(value);
    int bucket = hashCode % m_buckets.Length;
    #if FEATURE_RANDOMIZED_STRING_HASHING && !FEATURE_NETCORE
        int collisionCount = 0;
    #endif
    for (int i = m_buckets[hashCode % m_buckets.Length] - 1; i >= 0; i = m_slots[i].next) {
        if (m_slots[i].hashCode == hashCode && m_comparer.Equals(m_slots[i].value, value)) {
            return false;
        }
        #if FEATURE_RANDOMIZED_STRING_HASHING && !FEATURE_NETCORE
            collisionCount++;
        #endif
    }
 
    int index;
    if (m_freeList >= 0) {
        index = m_freeList;
        m_freeList = m_slots[index].next;
    }
    else {
        if (m_lastIndex == m_slots.Length) {
            IncreaseCapacity();
            // this will change during resize
            bucket = hashCode % m_buckets.Length;
        }
        index = m_lastIndex;
        m_lastIndex++;
    }
    m_slots[index].hashCode = hashCode;
    m_slots[index].value = value;
    m_slots[index].next = m_buckets[bucket] - 1;
    m_buckets[bucket] = index + 1;
    m_count++;
    m_version++;
 
    #if FEATURE_RANDOMIZED_STRING_HASHING && !FEATURE_NETCORE
        if (collisionCount > HashHelpers.HashCollisionThreshold && HashHelpers.IsWellKnownEqualityComparer(m_comparer)) {
            m_comparer = (IEqualityComparer<T>) HashHelpers.GetRandomizedEqualityComparer(m_comparer);
            SetCapacity(m_buckets.Length, true);
        }
    #endif // FEATURE_RANDOMIZED_STRING_HASHING
 
    return true;
}
```
可以注意到，在这段代码中，首先，会通过 `InternalGetHashCode()` 方法计算一个 HashCode。其中，`Lower31BitMask` 是一个常量 `0x7FFFFFFF` ：
```CSharp
private int InternalGetHashCode(T item) {
    if (item == null) {
        return 0;
    } 
    return m_comparer.GetHashCode(item) & Lower31BitMask;
}
```
接下来，在 HashSet 内部使用了`Slot` 这个结构来存储元素，该结构设计上类似于链表，每一个 `Slot` 中都记录对应元素的值、HashCode 以及下一个元素的索引。所以，只需要对它做一次遍历，如果对应元素的 HashCode 和 值 都相等，则认为该元素在 HashSet 中已经存在了。此时，`AddIfNotPresent()` 方法会返回 false。这就是 HashSet 去重的原理啦。在比较元素的值是否相等的时候，我们前面提到的 `IEqualityComparer<T>` 终于登场，它提供的 `Equals()` 方法恰好可以比较两个元素是否相等：
```CSharp
internal struct Slot {
    internal int hashCode;  // Lower 31 bits of hash code, -1 if unused
    internal int next;  // Index of next entry, -1 if last
    internal T value;
}

public interface IEqualityComparer<in T>
{
    bool Equals(T x, T y);
    int GetHashCode(T obj);                
}

```
再接下来，如果对应元素的 HashCode 或 值 都不相等，则认为该元素在 HashSet 中不存在。此时，需要考虑 HashSet 的容量是否足以放得下这个新元素。在容量不满足的情况下，就需要对 HashSet 进行扩容。值得一提的是，这里是使用质数进行扩容的：
```CSharp
private void IncreaseCapacity() {
    Debug.Assert(m_buckets != null, "IncreaseCapacity called on a set with no elements");
 
    int newSize = HashHelpers.ExpandPrime(m_count);
    if (newSize <= m_count) {
        throw new ArgumentException(SR.GetString(SR.Arg_HSCapacityOverflow));
    }
 
    // Able to increase capacity; copy elements to larger array and rehash
    SetCapacity(newSize, false);
}

public static int ExpandPrime(int oldSize)
{
    int newSize = 2 * oldSize;
 
    // Allow the hashtables to grow to maximum possible size (~2G elements) before encoutering capacity overflow.
    // Note that this check works even when _items.Length overflowed thanks to the (uint) cast
    if ((uint)newSize > MaxPrimeArrayLength && MaxPrimeArrayLength > oldSize)
    {
        Contract.Assert( MaxPrimeArrayLength == GetPrime(MaxPrimeArrayLength), "Invalid MaxPrimeArrayLength");
        return MaxPrimeArrayLength;
    }
 
    return GetPrime(newSize);
}
```

# IEqualityComparer<T>接口
OK，现在我们知道了，HashSet 之所以可以去重，一个重要的原因是 `IEqualityComparer<T>` 。而回到这个接口本身呢，它只有 `Equals()` 和 `GetHashCode()`，这其实非常符合我们的认知，因为这两个方法在对象相等的场景中十分常见，有一个准则是：如果重写了 `Equals()` 方法，那么，应该同时去重写 `GetHashCode()` 方法，即，两者在表达相等这个含义时应该具有一致性。这里可能会有一点疑问，那就是，我们平时使用 HashSet 的时候，完全不需要指定 `IEqualityComparer<T>` ，它一样可以正常工作啊？没错，这是因为微软提供了一个默认的实现：`EqualityComparer<T>.Default`。我们同样来看看它的实现：
```CSharp
private static EqualityComparer<T> CreateComparer() {
    Contract.Ensures(Contract.Result<EqualityComparer<T>>() != null);
 
    RuntimeType t = (RuntimeType)typeof(T);
    // Specialize type byte for performance reasons
    if (t == typeof(byte)) {
        return (EqualityComparer<T>)(object)(new ByteEqualityComparer());
    }
    // If T implements IEquatable<T> return a GenericEqualityComparer<T>
    if (typeof(IEquatable<T>).IsAssignableFrom(t)) {
        return (EqualityComparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(GenericEqualityComparer<int>), t);
    }
    // If T is a Nullable<U> where U implements IEquatable<U> return a NullableEqualityComparer<U>
    if (t.IsGenericType && t.GetGenericTypeDefinition() == typeof(Nullable<>)) {
        RuntimeType u = (RuntimeType)t.GetGenericArguments()[0];
        if (typeof(IEquatable<>).MakeGenericType(u).IsAssignableFrom(u)) {
            return (EqualityComparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(NullableEqualityComparer<int>), u);
        }
    }
            
    // See the METHOD__JIT_HELPERS__UNSAFE_ENUM_CAST and METHOD__JIT_HELPERS__UNSAFE_ENUM_CAST_LONG cases in getILIntrinsicImplementation
    if (t.IsEnum) {
        TypeCode underlyingTypeCode = Type.GetTypeCode(Enum.GetUnderlyingType(t));
 
        // Depending on the enum type, we need to special case the comparers so that we avoid boxing
        // Note: We have different comparers for Short and SByte because for those types we need to make sure we call GetHashCode on the actual underlying type as the 
        // implementation of GetHashCode is more complex than for the other types.
        switch (underlyingTypeCode) {
            case TypeCode.Int16: // short
               return (EqualityComparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(ShortEnumEqualityComparer<short>), t);
            case TypeCode.SByte:
                return (EqualityComparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(SByteEnumEqualityComparer<sbyte>), t);
            case TypeCode.Int32:
            case TypeCode.UInt32:
            case TypeCode.Byte:
            case TypeCode.UInt16: //ushort
                return (EqualityComparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(EnumEqualityComparer<int>), t);
            case TypeCode.Int64:
            case TypeCode.UInt64:
                return (EqualityComparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(LongEnumEqualityComparer<long>), t);
        }
    }
    // Otherwise return an ObjectEqualityComparer<T>
    return new ObjectEqualityComparer<T>();
}
```
在这里，`EqualityComparer<T>` 类是一个抽象类，实现了 `IEqualityComparer<T>` 接口。简单来说，对于简单类型如整型、字节型等，微软实现了相应的 `IEqualityComparer<T>` 接口；而对于复杂的类型，微软提供了 `ObjectEqualityComparer<T>` 这一实现：
```CSharp
internal class ObjectEqualityComparer<T>: EqualityComparer<T>
{
    [Pure]
    public override bool Equals(T x, T y) {
        if (x != null) {
            if (y != null) return x.Equals(y);
            return false;
        }
        if (y != null) return false;
        return true;
    }
 
    [Pure]
    public override int GetHashCode(T obj) {
        if (obj == null) return 0;
        return obj.GetHashCode();
    }
}
```
所以，现在又回到我们刚刚聊起的话题，为什么说一个类型的 `Equals()` 和 `GetHashCode()` 方法非常重要呢？因为如果我们不能正确地实现这两个方法，微软实现的这个  `ObjectEqualityComparer<T>` 就会出现问题，导致 HashSet 在判断元素是否存在时出现问题，所以，这是一系列的连锁反应。有人可能会问，博主你说的这个好夸张耶，像我就从来没有重写过这两个方法。OK，现在来回答我的一个问题，如果你定义了一个类型 `Foo` ，并尝试用它作为一个字典中的 Key ，那么，你觉得这个字典应该怎么判断这个 Key 是否存在呢？我觉得这是一个好问题，因为它引发了我们在 .NET 知识体系中的蝴蝶效应。

# 排序与去重是亲家
排序与去重，在我看来是亲家关系，因为两者都需要“比较”。所以，下面我想从 .NET 中选取一部分接口来阐述我的观点，以及当我们有了 LINQ 以后，是否就应该抛弃它们。可能这些接口大家平时都用不到多少，但我还是想花点时间来梳理这些知识盲点，因为我发现，与其为整个行业 35 岁的的职业生涯而焦虑，倒不如重新捡起这个行业的初心，好好地学一学数据结构、算法和数学。整个行业的火热，容易让每一个人都陷入一种“我非常厉害”的错觉，我写博客的时候，在心里想了这样一句话：**战士上战场，整天就知道 CRUD，连 HashSet 都不知道，早晚是个死**。用王布斯的口吻说出来，会不会有一种紧迫感呢？

## IEquatable<T>接口
`IEquatable<T>` 接口在微软官方文档中的定义是，**定义值类型或类实现的通用方法，以创建用于确定实例相等性的类型特定方法**。我承认，这不是一个特别好的定义，不过，我们可以换个角度来审视这个接口存在的意义。虽然 `Object` 这个基类提供了 `Equals()` 方法，但是这个方法只能接受一个 `object` 类型的参数， 所以，它本身会面临**类型安全性缺失**和**装箱**两个问题。为了解决这个问题，就必须要定义一个新的 `Equals()` 方法，确保它可以接收和当前类型一致的参数，所以就需要这样一个接口，你可以理解为它是 `Equals()` 方法的泛型版本，而众所周知 C# 是一门不支持多继承的语言，所以，这里只能以接口的形式提供出来。这里说一下我的结论，`IEquatable<T>` 接口对值类型更有用一点，相反，对引用类型就没有那么有用，因为它没有考虑到协变的问题，对引用类型的继承相对无力。下面是一个简单的例子：
```CSharp
//定义类型Foo，实现IEquatable<Foo>接口
public class Foo : IEquatable<Foo>
{
    public decimal Value { get; set; }
    public decimal Weight { get; set; }

    public override bool Equals(object other)
    {
        return Equals(other as Foo);
    }

    public bool Equals(Foo other)
    {
        if (other == null) return false;
        return (this.Value == other.Value && this.Weight == other.Weight);
    }
}

//平平无奇的代码
var foo1 = new Foo() { Value = 10, Weight = 1.0M };
var foo2 = new Foo() { Value = 10, Weight = 1.0M };
Assert.AreEqual(true, foo1.Equals(foo2));
```

## ICompareable/ICompareable<T>接口
`ICompareable` 和 `ICompareable<T>`是是同一个接口的非泛型与泛型版本，都需要实现 `CompareTo()` 方法。可能大家会觉得这几个接口都差不多啊，实际上，大家细心观察就能发现它们的区别，“相等”这一类的接口的返回值是布尔型，关注的是两个对象是否相等；而“比较”这一类的接口的返回值是整数型，关注的是哪个大哪个小。我们继续以 `Foo` 这个类型为例，分别实现`IComparerable`  和 `IComparerable<T>`两个接口：
```CSharp
//继续实现IComparable, IComparable<Foo>接口
public class Foo : IEquatable<Foo>, IComparable, IComparable<Foo>
{
    public decimal Value { get; set; }
    public decimal Weight { get; set; }

    public override bool Equals(object other)
    {
        return Equals(other as Foo);
    }

    public bool Equals(Foo other)
    {
        if (other == null) return false;
        return (this.Value == other.Value && this.Weight == other.Weight);
    }

    public int CompareTo(object obj)
    {
        var other = obj as Foo;
        return CompareTo(other);
    }

    public int CompareTo([AllowNull] Foo other)
    {
        if (other == null) return 1;
        return (int)((Value * Weight) - (other.Value * other.Weight));
    }
}

//平平无奇的代码
var foo1 = new Foo() { Value = 10, Weight = 1.0M };
var foo2 = new Foo() { Value = 20, Weight = 1.0M };
Assert.IsTrue(foo2.CompareTo(foo1) > 0);
```

## IComparer<T>接口
对于排序来说，理论上有`ICompareable` 和 `ICompareable<T>`这两个接口就可以了，为什么还要再定义一组接口呢？其实，我们结合生活中的场景就能想明白，不管是判断两个对象是否相等，还是对两个对象进行排序，这些条件都属于“变量”。`ICompareable` 和 `ICompareable<T>`这两个接口设计上的确没什么问题，但这都是一锤子买卖，一旦实现了对应的接口，就意味着如何比较两个对象的逻辑是确定好了的。可生活常识告诉我们，同一组信息不同的人考虑的维度是不一样的，譬如学生的成绩，可以按照某一个科目的成绩来排序，还可以按照各个科目的总成绩甚至是平均分来排序。对于上面的类型 `Foo`，我们不妨考虑按照 `Value` 和 `Weight` 分别进行排序，此时可以这样写：
```CSharp
//按Value排序
public class FooValueComparer : IComparer<Foo>
{
    public int Compare([AllowNull] Foo x, [AllowNull] Foo y)
    {
        if (x == null && y == null) return 0;
        if (x != null && y == null) return 1;
        if (x == null && y != null) return -1;
        return (int)(x.Value - y.Value);
    }
}

//按Weight排序
public class FooWeightComparer : IComparer<Foo>
{
    public int Compare([AllowNull] Foo x, [AllowNull] Foo y)
    {
        if (x == null && y == null) return 0;
        if (x != null && y == null) return 1;
        if (x == null && y != null) return -1;
        return (int)(x.Weight - y.Weight);
    }
}

//平平无奇的代码
var list= new List<Foo>{
    new Foo() { Value = 10, Weight = 2.0M },
    new Foo() { Value = 10, Weight = 1.0M }
};

//使用默认的排序器
list.Sort(); 

//按Value进行排序
list.Sort(new FooValueComparer());
list.OrderBy(x => x.Value);

//按Weight进行排序
list.Sort(new FooWeightComparer());
list.OrderBy(x => x.Weight);
```
在这里有一个点是，在不指定排序器的时候，微软帮我们提供了一个默认的排序器。而这个默认排序器会遵循这样的策略。如果类型 T 实现了 `IComparable<T>` 接口，则返回 `GenericComparer<int>` 实例；如果类型 T 实现是一个可空类型 `Nullable<U>` 并且类型 U 实现了 `IComparable<T>` 接口，则返回 `NullableComparer<int>` 实例；否则返回 `ObjectComparer<T>` 实例。
```CSharp
private static Comparer<T> CreateComparer() {
    RuntimeType t = (RuntimeType)typeof(T);
 
    // If T implements IComparable<T> return a GenericComparer<T>
    #if FEATURE_LEGACYNETCF
        // Pre-Apollo Windows Phone call the overload that sorts the keys, not values this achieves the same result
        if (CompatibilitySwitches.IsAppEarlierThanWindowsPhone8) {
            if (t.ImplementInterface(typeof(IComparable<T>))) {
                return (Comparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(GenericComparer<int>), t);
            }
        }
        else
    #endif
    if (typeof(IComparable<T>).IsAssignableFrom(t)) {
            return (Comparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(GenericComparer<int>), t);
    }
 
    // If T is a Nullable<U> where U implements IComparable<U> return a NullableComparer<U>
    if (t.IsGenericType && t.GetGenericTypeDefinition() == typeof(Nullable<>)) {
        RuntimeType u = (RuntimeType)t.GetGenericArguments()[0];
        if (typeof(IComparable<>).MakeGenericType(u).IsAssignableFrom(u)) {
            return (Comparer<T>)RuntimeTypeHandle.CreateInstanceForAnotherGenericParameter((RuntimeType)typeof(NullableComparer<int>), u);
        }
    }

    // Otherwise return an ObjectComparer<T>
    return new ObjectComparer<T>();
}
```
更有意思的是，`GenericComparer<T>` 就是利用 `IComparable<T>` 的 `CompareTo()` 方法来说实现的：
```CSharp
internal class GenericComparer<T> : Comparer<T> where T: IComparable<T>
{    
    public override int Compare(T x, T y) {
        if (x != null) {
            if (y != null) return x.CompareTo(y);
                return 1;
            }
        if (y != null) return -1;
        return 0;
    }
 
    // Equals method for the comparer itself. 
    public override bool Equals(Object obj){
        GenericComparer<T> comparer = obj as GenericComparer<T>;
        return comparer != null;
    }        
 
    public override int GetHashCode() {
        return this.GetType().Name.GetHashCode();
    }
}
```
在我们有了 `LINQ` 以后，通过 `OrderBy` 和 `OrderByDescending` 就可以进行排序，如果这个排序字段是一个简单类型，比如字符型、整型、日期型，这些简单类型微软都已经实现了相应的“排序”逻辑，而如果这个排序字段是一个复杂类型，比如一个自定义的类或者结构，此时，为了让这些方法能够“适应”这些复杂类型，最好的还是去实现 `IComparer<T>` 或者 `ICompareable<T>` 接口，然后传递给这两个排序方法。类似地，还有 `Distinct` 这个方法，它接收一个 `IEqualityComparer<T>` 类型的参数，所以，当你对一个列表进行去重(**Distinct**)操作时，千万不要想当然地人为它会按照你的期望去去重，如果结果不符合你的期望，很大原因是你没有给它提供一个合适的`IEqualityComparer<T>` 。所以，你看，我们绕了一大圈，从 HashSet 说到 `IEqualityComparer<T>`，又从排序说到去重，最终又回到了起点，这是多么有趣的一件事情。而去重(**Distinct**)这件事情，其实涉及到`Dictionary` 和 `HashSet` 两个数据结构，通过结构来推演性质，又通过性质来扫清盲点，这可能是这段时间刷 LeetCode 最大的一个收获吧！

# 本文小结
面试中偶然遇到的 HashSet 问题，让我发现自己的知识体系中存在着盲点。通过解读 HashSet 源代码，我们认识到 HashSet 可以去重的一个重要原因是`IEqualityComparer<T>` 接口，它决定了两个对象的实例在什么情况下可以被判定为相等。而这个接口，不单单在 HashSet 出现，在 Dictionary 中同样会出现，甚至在我们最熟悉不过的去重(**Distinct**)中还会出现，所以，通过 HashSet 这一个点上的疑问，我搞清楚了很多相关联的内容，这不是蝴蝶效应又是什么呢？而与去重(**Distinct**)相关联的则是排序，在此基础上，对 `IEquatable<T>` 接口、`ICompareable`/`ICompareable<T>` 接口、`IComparer<T>` 接口等知识盲点进行梳理。总而言之，排序需要关注的是 `ICompareable`/`ICompareable<T>` 接口、`IComparer<T>` 接口，去重需要关注的是 `IEqualityComparer<T>` 接口。好了，今天的这只蝴蝶就飞到这里，欢迎大家在博客中留言，谢谢大家！