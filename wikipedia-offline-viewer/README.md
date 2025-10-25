# Wikipedia Offline Viewer - Developer Skill Progression

This project demonstrates how the same task (creating a Wikipedia page downloader) would be implemented by developers at different skill levels, from Day 1 to 5 years of Python experience.

## Project Overview

Each version attempts to solve the same problem: download a Wikipedia page and save it for offline viewing. The implementations show realistic progression in:
- Code quality and organization
- Error handling
- Feature completeness
- Best practices
- Tool knowledge
- Problem-solving approaches

**Constraints for each developer:**
- 4 hours maximum to complete the task
- Access to the Internet (documentation, Stack Overflow, etc.)
- No AI assistance
- Started with 0 programming experience on Day 1

## Versions

### 📁 Day 1 - First Day Programming

**Experience:** ~4 hours total programming experience
**File:** `day1/wiki_download.py`

**Characteristics:**
- Just learned basic Python syntax
- Copy-pasted code from Stack Overflow without full understanding
- Hardcoded values
- Has a critical bug (trying to write bytes as string)
- No error handling
- Minimal comments, with typo
- Will crash when run

**Key Issues:**
```python
# Bug: webContent is bytes but trying to write as string
f.write(webContent)  # This will fail!
```

**How to run:**
```bash
cd day1
python wiki_download.py
# Will crash with TypeError
```

---

### 📁 Week 1 - One Week of Learning

**Experience:** ~30-40 hours of programming
**File:** `week1/wiki_downloader.py`

**Characteristics:**
- Learned about functions
- Uses user input for flexibility
- Discovered `with` statement for file handling
- Added basic try/except error handling (too broad)
- Fixed file mode issue (uses 'wb' correctly)
- Still simple but functional

**Improvements:**
- Code actually works
- Better file handling
- User interaction
- Basic error handling

**How to run:**
```bash
cd week1
python wiki_downloader.py
# Enter a Wikipedia URL when prompted
```

---

### 📁 Month 1 - One Month Experience

**Experience:** ~100-120 hours of programming
**File:** `month1/wikipedia_offline.py`

**Characteristics:**
- Learned about modern libraries (requests, BeautifulSoup)
- Better code organization with multiple functions
- Proper main() function and `if __name__ == "__main__"` pattern
- Specific exception handling
- Makes URLs absolute for better offline viewing
- Input validation
- Better documentation

**New Skills:**
- Using external libraries effectively
- HTML parsing with BeautifulSoup
- Modifying HTML for offline use
- Better code structure

**How to run:**
```bash
cd month1
pip install -r requirements.txt
python wikipedia_offline.py
```

---

### 📁 Year 1 - One Year Experience

**Experience:** ~500-800 hours of programming
**File:** `year1/wiki_archiver.py`

**Characteristics:**
- Object-oriented programming with classes
- Command-line arguments with argparse
- Logging instead of print statements
- Downloads CSS and images locally
- Creates proper directory structure
- Comprehensive docstrings
- Professional-looking code
- Progress indicators

**Advanced Features:**
- Complete offline viewing with assets
- Configurable via CLI
- Logging to track operations
- Session management with requests
- User-Agent headers

**How to run:**
```bash
cd year1
pip install -r requirements.txt
python wiki_archiver.py https://en.wikipedia.org/wiki/Python_(programming_language)
python wiki_archiver.py --help  # See all options
```

---

### 📁 Year 5 - Five Years Experience

**Experience:** ~5000-8000 hours of programming
**File:** `year5/wiki_archiver_pro.py`

**Characteristics:**
- Production-ready code
- Type hints throughout
- Async/await for concurrent downloads
- Retry logic with exponential backoff
- Progress bars with visual feedback
- Dataclasses for configuration
- Context managers for resource management
- Comprehensive error handling
- Logging to both console and file
- Extensive command-line options
- Professional documentation

**Production Features:**
- Asynchronous concurrent downloads (much faster)
- Semaphore to limit concurrent connections
- Hash-based filename generation
- Configurable retry logic
- Comprehensive statistics
- Proper resource cleanup
- Exception logging with tracebacks
- Keyboard interrupt handling

**How to run:**
```bash
cd year5
pip install -r requirements.txt
python wiki_archiver_pro.py https://en.wikipedia.org/wiki/Python_(programming_language)

# With options:
python wiki_archiver_pro.py https://en.wikipedia.org/wiki/Linux \
  -o linux_archive \
  --max-concurrent 20 \
  -v

# See all options:
python wiki_archiver_pro.py --help
```

---

### 📁 Guido - As Python's Creator Would Write It

**Experience:** Creator of Python (1989-present)
**File:** `guido/wiki_archiver.py`

**Philosophy:**
This implementation demonstrates how Guido van Rossum, Python's creator, might approach the task. It embodies the principles of **PEP 20 (The Zen of Python)** that he wrote:
- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Readability counts

**Characteristics:**
- **Type hints everywhere** - Guido championed PEP 484
- **Dataclasses** - Uses PEP 557 for clean data structures
- **Exceptional documentation** - Every function has clear docstrings explaining "why"
- **Pragmatic choices** - Uses best tools but doesn't over-engineer
- **Readability focus** - Code optimized for human understanding
- **Educational comments** - Inline notes explain Python best practices
- **PEP 8 compliant** - Perfect adherence to style guide
- **Synchronous approach** - Simpler is better for this use case

**What Makes This "Guido's Style":**
- Prefers clarity over cleverness
- Type hints as documentation and tooling support
- Comprehensive but concise docstrings
- Clean error handling with specific exceptions
- Uses standard library where reasonable (html.parser)
- Comments explain design decisions, not just code
- Single clear path through the code
- Proper Unix exit codes and signal handling

**Compared to Year 5 Version:**
The Year 5 developer uses async/await and complex optimization. Guido's version shows that **experienced developers know when NOT to use advanced features**. For this task:
- Synchronous code is simpler and sufficient
- Sequential downloads are fine for reasonable page sizes
- Readability matters more than peak performance
- Code should teach good practices

**How to run:**
```bash
cd guido
pip install -r requirements.txt
python wiki_archiver.py https://en.wikipedia.org/wiki/Python_(programming_language)

# See excellent help text:
python wiki_archiver.py --help

# Read the design notes:
cat DESIGN_NOTES.md
```

**Special Feature:**
Includes `DESIGN_NOTES.md` explaining the philosophy behind the implementation and how it embodies Python's design principles.

---

## Comparison Table

| Feature | Day 1 | Week 1 | Month 1 | Year 1 | Year 5 | Guido |
|---------|-------|--------|---------|--------|--------|-------|
| **Works** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Error Handling** | ❌ | Basic | Good | Excellent | Comprehensive | Exemplary |
| **User Input** | ❌ | Console | Console | CLI Args | CLI Args + Config | CLI Args |
| **External Libraries** | urllib | urllib | requests + BS4 | requests + BS4 | aiohttp + BS4 + tqdm | requests + BS4 |
| **Code Organization** | None | Functions | Functions + main | Classes + modules | Classes + types | Classes + types |
| **Downloads Assets** | ❌ | ❌ | Partial | ✅ CSS + Images | ✅ All assets | ✅ CSS + Images |
| **Documentation** | Minimal | Basic | Good | Excellent | Professional | Exemplary |
| **Performance** | N/A | Slow | Slow | Moderate | Fast (async) | Moderate |
| **Configurability** | None | Minimal | Basic | Good | Extensive | Focused |
| **Production Ready** | ❌ | ❌ | ❌ | Almost | ✅ | ✅ |
| **Type Hints** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ Complete |
| **Readability** | Poor | Fair | Good | Very Good | Good | Exceptional |
| **Educational Value** | Low | Low | Medium | High | High | Highest |

---

## Learning Progression

### Day 1 → Week 1
- **Key Learning:** Basic Python syntax, functions, file operations, user input
- **Main Improvement:** Code actually works

### Week 1 → Month 1
- **Key Learning:** External libraries, HTML parsing, code organization, specific exceptions
- **Main Improvement:** Professional structure and proper tools

### Month 1 → Year 1
- **Key Learning:** OOP, command-line tools, logging, proper architecture
- **Main Improvement:** True offline viewing with all assets

### Year 1 → Year 5
- **Key Learning:** Async programming, type hints, production practices, performance optimization
- **Main Improvement:** Production-ready, fast, and maintainable code

---

## Realistic Bugs and Issues

Each version contains realistic mistakes for that skill level:

1. **Day 1:** Critical bug - writing bytes as string
2. **Week 1:** Too broad exception handling (catches everything)
3. **Month 1:** External links won't work offline (partial solution)
4. **Year 1:** Sequential downloads are slow for many resources
5. **Year 5:** Requires understanding of async programming (learning curve)

---

## Running the Scripts

Each version can be run independently:

```bash
# Day 1 (will crash - intentional)
cd day1 && python wiki_download.py

# Week 1
cd week1 && python wiki_downloader.py

# Month 1 (requires dependencies)
cd month1
pip install -r requirements.txt
python wikipedia_offline.py

# Year 1 (requires dependencies)
cd year1
pip install -r requirements.txt
python wiki_archiver.py https://en.wikipedia.org/wiki/Python

# Year 5 (requires dependencies)
cd year5
pip install -r requirements.txt
python wiki_archiver_pro.py https://en.wikipedia.org/wiki/Python

# Guido (requires dependencies)
cd guido
pip install -r requirements.txt
python wiki_archiver.py https://en.wikipedia.org/wiki/Python
```

---

## Key Takeaways

1. **Skill progression is non-linear** - Early improvements are dramatic, later improvements are more subtle
2. **Working code comes quickly** - By week 1, basic functionality is achievable
3. **Professional quality takes time** - Production-ready code requires years of experience
4. **Different tools for different skills** - More experienced developers use more sophisticated tools
5. **Best practices are learned gradually** - Error handling, logging, testing, etc. come with experience
6. **Master developers know when to keep it simple** - Guido's version shows that the best code isn't always the most advanced; readability and maintainability often trump optimization

---

## Educational Purpose

This project is designed to:
- Show realistic skill progression in programming
- Demonstrate that early mistakes are normal and expected
- Illustrate how the same problem can be solved at different levels
- Encourage beginners by showing clear progression paths
- Help experienced developers remember their journey

---

## License

MIT License - Feel free to use for educational purposes

---

## Notes

- Each version represents a realistic implementation within a 4-hour timeframe
- Code reflects typical knowledge and patterns at each experience level
- Bugs and issues are intentionally realistic for each skill level
- Focus is on demonstrating progression, not perfect solutions
