"""
Backlog System Test Suite

Tests for backlog management system.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.backlog import (
    BacklogConfig,
    BacklogParser,
    Task,
    TaskStatus,
    Priority,
    BacklogRegistry,
    BacklogBuilder,
    BacklogWriter
)


class TestBacklogConfig:
    """Test backlog configuration"""
    
    def test_config_defaults(self):
        """Test default configuration"""
        config = BacklogConfig()
        
        assert config.enabled is True
        assert len(config.scan_paths) > 0
        assert config.include_todo_comments is True
    
    def test_config_todo_prefixes(self):
        """Test TODO prefixes"""
        config = BacklogConfig()
        
        assert 'TODO' in config.todo_prefixes
        assert 'BACKLOG' in config.todo_prefixes


class TestBacklogParser:
    """Test backlog parser"""
    
    def test_parser_initialization(self):
        """Test parser can be initialized"""
        config = BacklogConfig()
        parser = BacklogParser(config)
        
        assert parser is not None
    
    def test_parse_markdown_task(self, tmp_path):
        """Test parsing markdown tasks"""
        config = BacklogConfig()
        parser = BacklogParser(config)
        
        # Create test file
        test_file = tmp_path / "test_phase_01.md"
        test_file.write_text("""
# Phase 1

- [ ] Implement feature A
- [x] Complete feature B
- [ ] Add test coverage
""")
        
        tasks = parser.parse_file(test_file)
        
        assert len(tasks) == 3
        assert tasks[0].title == "Implement feature A"
        assert tasks[0].status == TaskStatus.TODO
        assert tasks[1].status == TaskStatus.DONE
    
    def test_parse_todo_comment(self, tmp_path):
        """Test parsing TODO comments"""
        config = BacklogConfig()
        parser = BacklogParser(config)
        
        # Create test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
# TODO: Fix bug in parser
# BACKLOG: Add unit tests
# Regular comment
# FIXME: Improve performance
""")
        
        tasks = parser.parse_file(test_file)
        
        assert len(tasks) == 3
        assert any("parser" in t.title.lower() for t in tasks)
    
    def test_phase_extraction(self, tmp_path):
        """Test phase number extraction"""
        config = BacklogConfig()
        parser = BacklogParser(config)
        
        test_file = tmp_path / "PHASE_37.md"
        test_file.write_text("- [ ] Test task")
        
        tasks = parser.parse_file(test_file)
        
        if tasks:
            assert tasks[0].phase == 37


class TestBacklogRegistry:
    """Test backlog registry"""
    
    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = BacklogRegistry()
        
        assert registry is not None
        assert len(registry.tasks) == 0
    
    def test_add_task(self):
        """Test adding task"""
        registry = BacklogRegistry()
        
        task = Task(
            id="TEMP-001",
            phase=1,
            title="Test task",
            module="test.py",
            priority=Priority.MEDIUM,
            status=TaskStatus.TODO,
            dependencies=[]
        )
        
        task_id = registry.add_task(task)
        
        assert task_id is not None
        assert len(registry.tasks) == 1
    
    def test_get_tasks_by_phase(self):
        """Test getting tasks by phase"""
        registry = BacklogRegistry()
        
        task1 = Task(
            id="TEMP-001",
            phase=1,
            title="Task 1",
            module=None,
            priority=Priority.LOW,
            status=TaskStatus.TODO,
            dependencies=[]
        )
        
        task2 = Task(
            id="TEMP-002",
            phase=2,
            title="Task 2",
            module=None,
            priority=Priority.LOW,
            status=TaskStatus.TODO,
            dependencies=[]
        )
        
        registry.add_task(task1)
        registry.add_task(task2)
        
        phase1_tasks = registry.get_tasks_by_phase(1)
        
        assert len(phase1_tasks) == 1
        assert phase1_tasks[0].title == "Task 1"
    
    def test_deduplication(self):
        """Test task deduplication"""
        registry = BacklogRegistry()
        
        task1 = Task(
            id="TEMP-001",
            phase=1,
            title="Duplicate task",
            module=None,
            priority=Priority.LOW,
            status=TaskStatus.TODO,
            dependencies=[]
        )
        
        task2 = Task(
            id="TEMP-002",
            phase=1,
            title="Duplicate task",
            module=None,
            priority=Priority.LOW,
            status=TaskStatus.TODO,
            dependencies=[]
        )
        
        registry.add_task(task1)
        registry.add_task(task2)
        
        # Should only have one task
        assert len(registry.tasks) == 1


class TestBacklogBuilder:
    """Test backlog builder"""
    
    def test_builder_initialization(self):
        """Test builder initialization"""
        config = BacklogConfig()
        builder = BacklogBuilder(config)
        
        assert builder is not None
    
    def test_build_returns_registry(self):
        """Test build returns registry"""
        config = BacklogConfig()
        config.scan_paths = []  # Don't scan anything
        
        builder = BacklogBuilder(config)
        registry = builder.build()
        
        assert isinstance(registry, BacklogRegistry)


class TestBacklogWriter:
    """Test backlog writer"""
    
    def test_writer_initialization(self):
        """Test writer initialization"""
        registry = BacklogRegistry()
        config = BacklogConfig()
        writer = BacklogWriter(registry, config)
        
        assert writer is not None
    
    def test_write_backlog(self, tmp_path):
        """Test writing backlog"""
        registry = BacklogRegistry()
        config = BacklogConfig()
        
        # Add some tasks
        task = Task(
            id="P01-T001",
            phase=1,
            title="Test task",
            module="test.py",
            priority=Priority.HIGH,
            status=TaskStatus.TODO,
            dependencies=[]
        )
        registry.add_task(task)
        
        writer = BacklogWriter(registry, config)
        output_file = tmp_path / "TEST_BACKLOG.md"
        
        result = writer.write(output_file)
        
        assert result.exists()
        content = result.read_text()
        assert "MERIDIAN v2.1.2" in content
        assert "Test task" in content


class TestIntegration:
    """Test backlog integration"""
    
    def test_complete_workflow(self, tmp_path):
        """Test complete backlog workflow"""
        # Setup test files
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()
        
        phase_file = test_dir / "PHASE_01.md"
        phase_file.write_text("""
# Phase 1

- [ ] Task A
- [ ] Task B
""")
        
        # Configure to scan test directory
        config = BacklogConfig()
        config.scan_paths = [str(test_dir)]
        
        # Build backlog
        builder = BacklogBuilder(config)
        registry = builder.build()
        
        # Should have extracted tasks
        assert len(registry.tasks) >= 2
        
        # Write backlog
        writer = BacklogWriter(registry, config)
        output_file = tmp_path / "BACKLOG.md"
        writer.write(output_file)
        
        assert output_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


